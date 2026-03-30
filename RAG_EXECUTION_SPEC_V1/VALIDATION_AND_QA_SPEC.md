# Validation and QA Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define QA checks and test scenarios before deployment

---

## 1. Overview

This specification defines **comprehensive validation and QA checks** to ensure safe deployment of the Micro Insurance Knowledge Base RAG system.

### Validation Layers

**Layer 1: Data Validation** (Pre-Ingestion)
- Chunk count verification
- Metadata completeness
- Safety flag correctness

**Layer 2: Ingestion Validation** (Post-Ingestion)
- Index completeness
- Embedding quality
- Metadata searchability

**Layer 3: Retrieval Validation** (System Testing)
- Retrieval quality
- Weight effectiveness
- Filtering correctness

**Layer 4: Answer Validation** (End-to-End Testing)
- Answer safety
- Disclaimer appropriateness
- Placeholder leak detection

**Layer 5: Production Validation** (Continuous Monitoring)
- Real-time leak detection
- Performance monitoring
- User feedback analysis

---

## 2. Layer 1: Data Validation (Pre-Ingestion)

### Check 1.1: Chunk Count Verification

**Purpose:** Verify all expected chunks present

**Test:**
```python
def test_chunk_counts():
    assert count_chunks('faq_chunks.jsonl') == 20, "FAQ count mismatch"
    assert count_chunks('rules_chunks.jsonl') == 27, "Rules count mismatch"
    assert count_chunks('plans_chunks.jsonl') == 10, "Plans count mismatch"
    assert count_chunks('network_chunks.jsonl') == 10, "Network count mismatch"
    assert count_chunks('mapping_reference.jsonl') == 20, "Mapping count mismatch"
    
    total = 20 + 27 + 10 + 10 + 20
    assert total == 87, "Total count should be 87"
```

**Pass Criteria:** All counts match expected

**Deployment Blocker if Failed:** YES (data integrity issue)

---

### Check 1.2: Metadata Completeness

**Purpose:** Verify all required metadata fields present

**Test:**
```python
REQUIRED_FIELDS = [
    'chunk_id', 'chunk_type', 'source_file', 'source_id', 'text', 'status',
    'is_placeholder', 'safe_for_client_direct_use', 'retrieval_weight_hint',
    'requires_plan_confirmation', 'requires_network_verification',
    'ingestion_priority', 'confidence'
]

def test_metadata_completeness():
    for chunk in all_chunks:
        for field in REQUIRED_FIELDS:
            assert field in chunk, f"Missing field {field} in {chunk['chunk_id']}"
            assert chunk[field] is not None, f"Null value for {field} in {chunk['chunk_id']}"
```

**Pass Criteria:** All required fields present and non-null

**Deployment Blocker if Failed:** YES (metadata incomplete)

---

### Check 1.3: Placeholder Flag Correctness

**Purpose:** Verify all Plans/Network tagged as placeholders

**Test:**
```python
def test_placeholder_flags():
    # All Plans MUST be placeholders
    plans = [c for c in all_chunks if c['chunk_type'] == 'Plans']
    assert len(plans) == 10, "Plans count mismatch"
    for chunk in plans:
        assert chunk['is_placeholder'] == True, f"{chunk['chunk_id']} missing placeholder flag"
        assert chunk['safe_for_client_direct_use'] == False, f"{chunk['chunk_id']} incorrectly marked safe"
    
    # All Network MUST be placeholders
    network = [c for c in all_chunks if c['chunk_type'] == 'Network']
    assert len(network) == 10, "Network count mismatch"
    for chunk in network:
        assert chunk['is_placeholder'] == True, f"{chunk['chunk_id']} missing placeholder flag"
        assert chunk['safe_for_client_direct_use'] == False, f"{chunk['chunk_id']} incorrectly marked safe"
    
    # All FAQ/Rules/Mapping MUST NOT be placeholders
    non_placeholders = [c for c in all_chunks if c['chunk_type'] in ['FAQ', 'Rules', 'Mapping']]
    assert len(non_placeholders) == 67, "Non-placeholder count mismatch"
    for chunk in non_placeholders:
        assert chunk['is_placeholder'] == False, f"{chunk['chunk_id']} incorrectly marked placeholder"
```

**Pass Criteria:** All placeholder flags correct

**Deployment Blocker if Failed:** YES (CRITICAL - legal liability risk)

---

### Check 1.4: Retrieval Weight Range

**Purpose:** Verify weights in valid range

**Test:**
```python
def test_weight_range():
    for chunk in all_chunks:
        weight = chunk['retrieval_weight_hint']
        assert 0.0 <= weight <= 1.0, f"{chunk['chunk_id']} weight out of range: {weight}"
        
        # Placeholders MUST have low weight
        if chunk['is_placeholder']:
            assert weight <= 0.3, f"{chunk['chunk_id']} placeholder weight too high: {weight}"
```

**Pass Criteria:** All weights in valid range, placeholders ≤0.3

**Deployment Blocker if Failed:** YES (retrieval safety)

---

### Check 1.5: Cross-Field Consistency

**Purpose:** Verify metadata fields consistent with each other

**Test:**
```python
def test_cross_field_consistency():
    for chunk in all_chunks:
        # Rule: is_placeholder=true → safe_for_client_direct_use=false
        if chunk['is_placeholder']:
            assert not chunk['safe_for_client_direct_use'], \
                f"{chunk['chunk_id']}: placeholder marked safe"
        
        # Rule: is_placeholder=true → weight ≤ 0.3
        if chunk['is_placeholder']:
            assert chunk['retrieval_weight_hint'] <= 0.3, \
                f"{chunk['chunk_id']}: placeholder weight too high"
        
        # Rule: chunk_type=Plans → plan_id present
        if chunk['chunk_type'] == 'Plans':
            assert 'plan_id' in chunk and chunk['plan_id'], \
                f"{chunk['chunk_id']}: missing plan_id"
        
        # Rule: chunk_type=Network → provider_id present
        if chunk['chunk_type'] == 'Network':
            assert 'provider_id' in chunk and chunk['provider_id'], \
                f"{chunk['chunk_id']}: missing provider_id"
```

**Pass Criteria:** All cross-field rules satisfied

**Deployment Blocker if Failed:** YES (metadata integrity)

---

## 3. Layer 2: Ingestion Validation (Post-Ingestion)

### Check 2.1: Index Completeness

**Purpose:** Verify all chunks indexed in vector database

**Test:**
```python
def test_index_completeness():
    indexed_count = vector_db.count()
    expected_count = 67  # Phase B: FAQ+Rules+Mapping only
    # Or 87 for Phase C: all chunks
    
    assert indexed_count == expected_count, \
        f"Index count mismatch. Expected {expected_count}, got {indexed_count}"
    
    # Verify each chunk retrievable by ID
    for chunk in expected_chunks:
        result = vector_db.get_by_id(chunk['chunk_id'])
        assert result is not None, f"{chunk['chunk_id']} not found in index"
```

**Pass Criteria:** All expected chunks indexed and retrievable

**Deployment Blocker if Failed:** YES (indexing failure)

---

### Check 2.2: Metadata Searchability

**Purpose:** Verify metadata filters work correctly

**Test:**
```python
def test_metadata_filters():
    # Test is_placeholder filter
    non_placeholders = vector_db.query("insurance", filter={"is_placeholder": False}, top_k=100)
    for result in non_placeholders:
        assert not result['is_placeholder'], "Placeholder leaked through filter"
    
    # Test chunk_type filter
    faqs = vector_db.query("insurance", filter={"chunk_type": "FAQ"}, top_k=100)
    for result in faqs:
        assert result['chunk_type'] == 'FAQ', "Non-FAQ in FAQ filter"
    
    # Test status filter
    approved = vector_db.query("insurance", filter={"status": "Approved"}, top_k=100)
    for result in approved:
        assert result['status'] == 'Approved', "Non-Approved in Approved filter"
```

**Pass Criteria:** All metadata filters work correctly

**Deployment Blocker if Failed:** YES (filtering broken)

---

### Check 2.3: Embedding Quality

**Purpose:** Verify embeddings capture semantic meaning

**Test:**
```python
def test_embedding_quality():
    # Test 1: Similar questions should retrieve same FAQ
    query1 = "What is a deductible?"
    query2 = "Can you explain deductibles to me?"
    
    results1 = vector_db.query(query1, top_k=1)
    results2 = vector_db.query(query2, top_k=1)
    
    assert results1[0]['chunk_id'] == results2[0]['chunk_id'], \
        "Similar queries should retrieve same chunk"
    
    # Test 2: Dissimilar questions should retrieve different FAQ
    query3 = "How do I file a claim?"
    results3 = vector_db.query(query3, top_k=1)
    
    assert results3[0]['chunk_id'] != results1[0]['chunk_id'], \
        "Dissimilar queries should retrieve different chunks"
```

**Pass Criteria:** Embeddings capture semantic similarity

**Deployment Blocker if Failed:** WARN (may need embedding model tuning)

---

## 4. Layer 3: Retrieval Validation (System Testing)

### Check 3.1: FAQ Retrieval Relevance

**Purpose:** Verify FAQ chunks retrieved for FAQ questions

**Test:**
```python
FAQ_TEST_QUERIES = [
    ("What is a deductible?", "FAQ-001"),
    ("How do I file a claim?", "FAQ-002"),
    ("What is a copay?", "FAQ-003"),
    ("What is coinsurance?", "FAQ-004"),
    # ... 50 total test queries
]

def test_faq_retrieval_relevance():
    correct = 0
    total = len(FAQ_TEST_QUERIES)
    
    for query, expected_chunk_id in FAQ_TEST_QUERIES:
        results = vector_db.query(query, filter={"chunk_type": "FAQ"}, top_k=10)
        retrieved_ids = [r['chunk_id'] for r in results]
        
        if expected_chunk_id in retrieved_ids:
            correct += 1
    
    relevance = correct / total
    assert relevance >= 0.85, f"FAQ relevance too low: {relevance:.2%}"
```

**Pass Criteria:** FAQ retrieval relevance ≥85%

**Deployment Blocker if Failed:** YES (retrieval quality)

---

### Check 3.2: Weight Hierarchy Enforcement

**Purpose:** Verify FAQ scores higher than placeholders despite semantic match

**Test:**
```python
def test_weight_hierarchy():
    # Query that matches both FAQ and placeholder semantically
    query = "Does Basic Family Plan cover dental?"
    
    results = vector_db.query(query, top_k=20)
    
    # Find FAQ and placeholder in results
    faq_position = None
    placeholder_position = None
    
    for i, result in enumerate(results):
        if result['chunk_type'] == 'FAQ' and 'dental' in result['text'].lower():
            faq_position = i
        if result['is_placeholder'] and 'plan' in result['text'].lower():
            placeholder_position = i
    
    # FAQ should rank higher than placeholder
    if faq_position is not None and placeholder_position is not None:
        assert faq_position < placeholder_position, \
            f"Placeholder ranked higher than FAQ! FAQ position: {faq_position}, Placeholder position: {placeholder_position}"
```

**Pass Criteria:** FAQ always ranks higher than placeholders

**Deployment Blocker if Failed:** YES (CRITICAL - trust hierarchy violated)

---

### Check 3.3: Placeholder Downranking

**Purpose:** Verify placeholders rank very low (typically >position 20)

**Test:**
```python
def test_placeholder_downranking():
    test_queries = [
        "What does my plan cover?",
        "Is this provider in-network?",
        "Tell me about the Basic Family Plan",
        # ... 20 total queries
    ]
    
    placeholder_in_top_10_count = 0
    total_queries = len(test_queries)
    
    for query in test_queries:
        results = vector_db.query(query, top_k=10)
        
        for result in results:
            if result['is_placeholder']:
                placeholder_in_top_10_count += 1
                break  # Count query, not individual placeholders
    
    placeholder_rate = placeholder_in_top_10_count / total_queries
    assert placeholder_rate <= 0.1, \
        f"Placeholders appearing too frequently in top-10: {placeholder_rate:.2%}"
```

**Pass Criteria:** Placeholders appear in <10% of top-10 results (ideally 0%)

**Deployment Blocker if Failed:** YES (placeholder risk)

---

### Check 3.4: Chunk Type Distribution

**Purpose:** Verify FAQ/Rules dominant in retrieval results

**Test:**
```python
def test_chunk_type_distribution():
    test_queries = [
        "What is a deductible?",
        "How do I file a claim?",
        # ... 50 total general insurance queries
    ]
    
    chunk_type_counts = {"FAQ": 0, "Rules": 0, "Mapping": 0, "Plans": 0, "Network": 0}
    total_retrieved = 0
    
    for query in test_queries:
        results = vector_db.query(query, top_k=10)
        for result in results:
            chunk_type_counts[result['chunk_type']] += 1
            total_retrieved += 1
    
    faq_rules_pct = (chunk_type_counts['FAQ'] + chunk_type_counts['Rules']) / total_retrieved
    
    assert faq_rules_pct >= 0.70, \
        f"FAQ+Rules should be >70% of top-10 results. Got {faq_rules_pct:.2%}"
```

**Pass Criteria:** FAQ + Rules ≥70% of top-10 results

**Deployment Blocker if Failed:** WARN (content quality issue)

---

### Check 3.5: Filtering Correctness

**Purpose:** Verify customer-facing filtering excludes placeholders

**Test:**
```python
def test_customer_facing_filtering():
    test_queries = [
        "What is my plan coverage?",
        "Is this hospital in-network?",
        "What does the Basic Family Plan include?",
        # ... 20 total plan/network queries
    ]
    
    for query in test_queries:
        # Customer-facing retrieval: exclude placeholders
        results = vector_db.query(query, filter={"is_placeholder": False}, top_k=10)
        
        # Verify NO placeholders in results
        for result in results:
            assert not result['is_placeholder'], \
                f"Placeholder leaked in customer-facing retrieval for query: {query}"
```

**Pass Criteria:** 0 placeholders in customer-facing retrieval

**Deployment Blocker if Failed:** YES (CRITICAL - placeholder leak risk)

---

## 5. Layer 4: Answer Validation (End-to-End Testing)

### Check 4.1: Answer Safety - Placeholder Leak Detection

**Purpose:** Verify NO placeholder content in customer answers

**Test:**
```python
def test_placeholder_leak_in_answers():
    test_queries = [
        "Does my Basic Family Plan cover dental?",
        "Is Dubai Medical Center in-network?",
        "What does the Premium Corporate Plan cost?",
        # ... 30 total plan/network queries
    ]
    
    for query in test_queries:
        # Generate answer (end-to-end)
        answer, sources = generate_answer(query, use_case="customer-facing")
        
        # Check sources for placeholders
        for source in sources:
            assert not source['is_placeholder'], \
                f"Placeholder appeared in answer sources for query: {query}\nSource: {source['chunk_id']}"
        
        # Check answer text for placeholder IDs (shouldn't appear)
        placeholder_ids = ['PLAN-003', 'PROV-001', 'NETWORK-001']  # Example IDs
        for placeholder_id in placeholder_ids:
            assert placeholder_id not in answer, \
                f"Placeholder ID {placeholder_id} appeared in answer text for query: {query}"
```

**Pass Criteria:** 0% placeholder leak rate

**Deployment Blocker if Failed:** YES (CRITICAL - legal liability)

---

### Check 4.2: Disclaimer Appropriateness

**Purpose:** Verify appropriate disclaimers added for plan/network questions

**Test:**
```python
DISCLAIMER_KEYWORDS = [
    "check your policy documents",
    "contact customer service",
    "verify before",
    "coverage varies by plan",
    "provider network participation can change"
]

def test_disclaimer_presence():
    plan_queries = [
        "Does my plan cover dental?",
        "What is my deductible?",
        "Is dental covered?",
        # ... 20 total plan-specific queries
    ]
    
    for query in plan_queries:
        answer, sources = generate_answer(query, use_case="customer-facing")
        
        # Check if disclaimer present
        has_disclaimer = any(keyword in answer.lower() for keyword in DISCLAIMER_KEYWORDS)
        
        assert has_disclaimer, \
            f"Missing disclaimer for plan-specific query: {query}\nAnswer: {answer}"
```

**Pass Criteria:** Disclaimers present for 100% of plan/network questions

**Deployment Blocker if Failed:** YES (compliance risk)

---

### Check 4.3: Answer Confidence by Source Mix

**Purpose:** Verify answer confidence reflects weakest link

**Test:**
```python
def test_answer_confidence_weakest_link():
    # Scenario 1: FAQ (High) + Rule (High) → OVERALL High
    answer1, sources1 = generate_answer("What is a deductible?")
    assert sources1[0]['chunk_type'] == 'FAQ' and sources1[1]['chunk_type'] == 'Rules'
    assert get_overall_confidence(sources1) == 'HIGH'
    
    # Scenario 2: FAQ (High) + Placeholder (Very Low) → OVERALL Moderate (with disclaimer)
    answer2, sources2 = generate_answer("Does my Basic Family Plan cover dental?")
    has_placeholder = any(s['is_placeholder'] for s in sources2)
    if has_placeholder:
        # Overall confidence should be moderate (weakest link)
        assert get_overall_confidence(sources2) in ['MODERATE', 'LOW']
        # Disclaimer should be present
        assert "check your policy" in answer2.lower()
```

**Pass Criteria:** Answer confidence reflects weakest source

**Deployment Blocker if Failed:** WARN (answer safety behavior issue)

---

### Check 4.4: Direct Use Safety

**Purpose:** Verify safe_for_client_direct_use=false chunks not shown directly to customers

**Test:**
```python
def test_direct_use_safety():
    # Mapping chunks should not be displayed directly
    mapping_queries = [
        "Show me all mapping information",
        "What are the relationships?",
    ]
    
    for query in mapping_queries:
        answer, sources = generate_answer(query, use_case="customer-facing")
        
        # Mapping may be retrieved for context, but NOT displayed in answer
        mapping_sources = [s for s in sources if s['chunk_type'] == 'Mapping']
        if mapping_sources:
            # Verify mapping text not copied verbatim into answer
            for mapping in mapping_sources:
                assert mapping['text'] not in answer, \
                    "Mapping text displayed directly in answer"
```

**Pass Criteria:** safe_for_client_direct_use=false chunks never displayed directly

**Deployment Blocker if Failed:** YES (display safety)

---

### Check 4.5: Source Traceability

**Purpose:** Verify answers traceable to source chunks and files

**Test:**
```python
def test_source_traceability():
    query = "What is a deductible?"
    answer, sources = generate_answer(query)
    
    # Verify sources present
    assert len(sources) > 0, "No sources returned"
    
    # Verify each source has traceability fields
    for source in sources:
        assert 'chunk_id' in source and source['chunk_id']
        assert 'source_file' in source and source['source_file']
        assert 'source_id' in source and source['source_id']
    
    # Verify sources can be traced back to original files
    for source in sources:
        original_file = f"data/{source['source_file']}"
        assert os.path.exists(original_file), f"Source file not found: {original_file}"
```

**Pass Criteria:** All answers traceable to source files

**Deployment Blocker if Failed:** WARN (traceability for compliance)

---

## 6. Layer 5: Production Validation (Continuous Monitoring)

### Check 5.1: Real-Time Placeholder Leak Detection

**Purpose:** Monitor production for placeholder leaks

**Implementation:**
```python
def monitor_placeholder_leaks_realtime():
    # Called after every customer answer generation
    if production_answer_generated:
        for source in answer_sources:
            if source['is_placeholder']:
                alert_critical("PLACEHOLDER LEAK DETECTED!")
                log_incident({
                    "query": user_query,
                    "answer": generated_answer,
                    "placeholder_source": source['chunk_id'],
                    "timestamp": datetime.now()
                })
                # Optional: Suppress answer, show fallback
```

**Alert Threshold:** Any detection = CRITICAL alert

**Response:** Immediate investigation within 1 hour

---

### Check 5.2: Retrieval Weight Distribution Monitoring

**Purpose:** Track chunk type distribution in production queries

**Implementation:**
```python
def monitor_retrieval_distribution_daily():
    # Aggregate last 24 hours
    chunk_type_counts = get_chunk_type_distribution_last_24h()
    
    faq_rules_pct = (chunk_type_counts['FAQ'] + chunk_type_counts['Rules']) / total_chunks_retrieved
    
    if faq_rules_pct < 0.70:
        alert_medium(f"FAQ+Rules distribution low: {faq_rules_pct:.2%}")
    
    placeholder_pct = (chunk_type_counts['Plans'] + chunk_type_counts['Network']) / total_chunks_retrieved
    
    if placeholder_pct > 0.05:
        alert_high(f"Placeholder distribution high: {placeholder_pct:.2%}")
```

**Alert Threshold:** FAQ+Rules <70% or Placeholders >5%

**Response:** Review within 24 hours

---

### Check 5.3: Answer Quality Monitoring

**Purpose:** Track answer quality by source type

**Implementation:**
```python
def monitor_answer_quality_weekly():
    # Sample 100 customer interactions from last week
    interactions = sample_interactions(100)
    
    for interaction in interactions:
        # Analyze source mix
        source_types = [s['chunk_type'] for s in interaction['sources']]
        
        # Track answer quality by source mix
        if 'FAQ' in source_types:
            faq_answer_quality_scores.append(interaction['quality_score'])
        
        if any(s['is_placeholder'] for s in interaction['sources']):
            placeholder_answer_quality_scores.append(interaction['quality_score'])
    
    avg_faq_quality = mean(faq_answer_quality_scores)
    avg_placeholder_quality = mean(placeholder_answer_quality_scores)
    
    if avg_faq_quality < 4.0:
        alert_medium(f"FAQ answer quality low: {avg_faq_quality:.2f}/5.0")
```

**Alert Threshold:** FAQ quality <4.0/5.0

**Response:** Review FAQ content, update low-quality chunks

---

### Check 5.4: User Feedback Analysis

**Purpose:** Collect user feedback to identify issues

**Implementation:**
```python
def analyze_user_feedback_weekly():
    # Collect thumbs up/down, comments
    feedback = get_user_feedback_last_week()
    
    negative_feedback = [f for f in feedback if f['rating'] == 'thumbs_down']
    
    # Identify common themes
    for feedback_item in negative_feedback:
        query = feedback_item['query']
        answer = feedback_item['answer']
        sources = feedback_item['sources']
        
        # Check if placeholder-related
        if any(s['is_placeholder'] for s in sources):
            log_placeholder_related_issue(feedback_item)
        
        # Check if disclaimer-related
        if "check your policy" in answer and "too vague" in feedback_item['comment']:
            log_disclaimer_related_issue(feedback_item)
```

**Alert Threshold:** >10% negative feedback rate

**Response:** Investigate common themes, improve content

---

## 7. Validation Test Scenarios

### Scenario 1: General Insurance Question
**Query:** "What is a deductible?"  
**Expected Behavior:**
- FAQ-001 retrieved (top-1)
- RULE-001 retrieved (top-5)
- Answer confident, clear explanation
- No disclaimers needed

**Validation:**
- ✅ FAQ in top-1
- ✅ Answer quality HIGH
- ✅ No placeholder leak

---

### Scenario 2: Plan-Specific Question (with Placeholder)
**Query:** "Does my Basic Family Plan cover dental?"  
**Expected Behavior:**
- FAQ-005 retrieved (top-1)
- RULE-003 retrieved (top-5)
- PLAN-003 placeholder downranked (position >20) or filtered out
- Answer provides general guidance + disclaimer

**Validation:**
- ✅ FAQ in top-1
- ✅ Placeholder filtered out OR heavily downranked
- ✅ Disclaimer present ("Check your policy documents")
- ✅ NO placeholder content stated as fact

---

### Scenario 3: Network Question (with Placeholder)
**Query:** "Is Dubai Medical Center in-network?"  
**Expected Behavior:**
- FAQ-015 retrieved (top-1)
- PROV-001 placeholder downranked or filtered out
- Answer provides verification process + disclaimer

**Validation:**
- ✅ FAQ in top-1
- ✅ Network status NOT confirmed
- ✅ Disclaimer present ("Verify before appointment")
- ✅ NO placeholder network status stated

---

### Scenario 4: Operational Question (Pending Detail)
**Query:** "How do I refill a prescription?"  
**Expected Behavior:**
- FAQ-011 (Pending Detail) retrieved
- Answer provides general guidance
- Operational disclaimer added

**Validation:**
- ✅ FAQ-011 retrieved
- ✅ General guidance provided
- ✅ Disclaimer present ("Contact customer service for specific instructions")

---

### Scenario 5: Policy Question (Rule-only)
**Query:** "What happens if I don't disclose a pre-existing condition?"  
**Expected Behavior:**
- RULE-008 (Needs Review) retrieved
- No FAQ match
- Answer provides policy guidance + caution disclaimer

**Validation:**
- ✅ RULE-008 retrieved
- ✅ Policy guidance provided
- ✅ Caution disclaimer present ("For personalized guidance, contact compliance team")

---

## 8. Pass Criteria Summary

| Check | Pass Criteria | Deployment Blocker? |
|-------|---------------|---------------------|
| **1.1** Chunk Count | All counts match expected (87 total) | YES |
| **1.2** Metadata Completeness | All required fields present | YES |
| **1.3** Placeholder Flags | All Plans/Network = is_placeholder:true | YES (CRITICAL) |
| **1.4** Weight Range | All weights 0.0-1.0, placeholders ≤0.3 | YES |
| **1.5** Cross-Field Consistency | All consistency rules satisfied | YES |
| **2.1** Index Completeness | All chunks indexed and retrievable | YES |
| **2.2** Metadata Searchability | All filters work correctly | YES |
| **2.3** Embedding Quality | Semantic similarity captured | WARN |
| **3.1** FAQ Relevance | ≥85% relevance | YES |
| **3.2** Weight Hierarchy | FAQ ranks higher than placeholders | YES (CRITICAL) |
| **3.3** Placeholder Downranking | Placeholders <10% of top-10 | YES |
| **3.4** Chunk Type Distribution | FAQ+Rules ≥70% of top-10 | WARN |
| **3.5** Filtering Correctness | 0% placeholders in customer-facing | YES (CRITICAL) |
| **4.1** Placeholder Leak | 0% leak rate | YES (CRITICAL) |
| **4.2** Disclaimer Presence | 100% for plan/network questions | YES |
| **4.3** Answer Confidence | Reflects weakest link | WARN |
| **4.4** Direct Use Safety | safe:false not displayed directly | YES |
| **4.5** Source Traceability | All answers traceable | WARN |
| **5.1** Real-Time Leak Detection | 0% leak rate (continuous) | CRITICAL |
| **5.2** Weight Distribution | FAQ+Rules ≥70% (daily) | MEDIUM |
| **5.3** Answer Quality | FAQ quality ≥4.0/5.0 (weekly) | MEDIUM |
| **5.4** User Feedback | <10% negative rate (weekly) | LOW |

---

## 9. Deployment Readiness Checklist

### Pre-Deployment (All Must Pass)
- [ ] All data validation checks passed (1.1-1.5)
- [ ] All ingestion validation checks passed (2.1-2.2)
- [ ] All retrieval validation checks passed (3.1-3.5)
- [ ] All answer validation checks passed (4.1-4.5)
- [ ] Test scenarios 1-5 executed successfully
- [ ] Placeholder leak detection implemented and tested
- [ ] Monitoring and alerting configured
- [ ] Rollback procedure documented and tested
- [ ] Compliance approval obtained

### Post-Deployment (Continuous Monitoring)
- [ ] Real-time leak detection active
- [ ] Daily weight distribution monitoring
- [ ] Weekly answer quality monitoring
- [ ] Weekly user feedback analysis
- [ ] Quarterly compliance audit scheduled

---

## 10. Document Control

**Filename:** VALIDATION_AND_QA_SPEC.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- METADATA_APPLICATION_SPEC.md - Metadata requirements
- CHUNK_FILTERING_RULES.md - Filtering requirements
- RETRIEVAL_WEIGHTING_SPEC.md - Weight requirements
- PLACEHOLDER_ENFORCEMENT_SPEC.md - Placeholder rules
- ANSWER_SAFETY_BEHAVIOR.md - Answer requirements
- DEPLOYMENT_READINESS_GATES.md - Go/No-Go criteria

---

**END OF VALIDATION AND QA SPECIFICATION**

**CRITICAL REMINDER:** Validation is not optional. Every check exists to prevent production issues.
