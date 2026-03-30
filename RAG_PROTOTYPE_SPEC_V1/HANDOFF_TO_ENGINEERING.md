# Handoff to Engineering

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document provides **clear handoff guidance for engineering teams implementing the Phase 1 RAG prototype**. It summarizes what to build first, what safeguards are mandatory, what should remain disabled, and what evidence to provide before proceeding to Phase 2.

**Audience:** Engineering/implementation teams, AI/ML engineers, future Copilot agents, contractors

---

## Implementation Summary

**Build:** Internal RAG prototype retrieval system per specification  
**Timeline:** 2-3 weeks implementation + 2-3 weeks testing = **4-6 weeks total Phase 1**  
**Scope:** Internal testing only, NOT customer-facing  
**Technology Stack:** Your choice (spec is technology-agnostic)  
**Critical Requirement:** **Zero placeholder leakage - placeholders NEVER stated as facts**

---

## What to Implement First

### Priority 1: Core Retrieval System (Week 1)

**Implement in this order:**

#### Step 1: Ingest FAQ Chunks (Day 1-2)
- **Source:** `faq_chunks.jsonl` (20 chunks)
- **Action:**
  - Load all FAQ chunks with status=[Approved, Active]
  - Generate embeddings (your choice of model: OpenAI, Cohere, open-source)
  - Index in vector database (your choice: Pinecone, Weaviate, pgvector, Chroma, etc.)
  - Validate metadata preserved: chunk_id, chunk_type, status, confidence, safe_for_client_direct_use, retrieval_weight
- **Validation:**
  - All 20 FAQ chunks indexed
  - Test query "What is a deductible?" retrieves FAQ-001 in top 3
  - Metadata complete for all chunks

#### Step 2: Ingest Rules Chunks (Day 2-3)
- **Source:** `rules_chunks.jsonl` (27 chunks)
- **Action:**
  - Load all Rules chunks with status=[Approved, Active]
  - Generate embeddings, index in vector DB
  - Validate metadata preserved
- **Validation:**
  - All 27 Rules chunks indexed
  - Test query "Are pre-existing conditions covered?" retrieves FAQ-008 + RULE-007
  - Semantic search working across FAQ + Rules

#### Step 3: Ingest Mapping Chunks (Day 3-4)
- **Source:** `mapping_reference.jsonl` (20 chunks)
- **Action:**
  - Load all Mapping chunks
  - Generate embeddings, index in vector DB
  - Validate metadata preserved
- **Validation:**
  - All 20 Mapping chunks indexed
  - Total indexed: 67 strong chunks (FAQ + Rules + Mapping)

---

#### Step 4: Apply Placeholder Ingest with Penalties (Day 4-5)
- **Source:** `plans_chunks.jsonl` (10 chunks) + `network_chunks.jsonl` (10 chunks)
- **Action:**
  - Load ALL Plans and Network chunks (even though placeholders)
  - **CRITICAL:** Apply downweighting penalty ×0.08
  - Set `retrieval_priority=VERY LOW`
  - Validate `is_placeholder=TRUE` flag present
  - Validate `safe_for_client_direct_use=FALSE` flag present
  - Calculate expected final score: semantic_score × retrieval_weight × 0.08
- **Validation:**
  - All 20 placeholder chunks indexed with penalties
  - **CRITICAL TEST:** Query "What is a deductible?" should retrieve FAQ-001 (score ~0.9) NOT PLAN-003 placeholder (score <0.1 after penalty)
  - **CRITICAL TEST:** Query "Does Basic Family Plan cover dental?" should retrieve FAQ-005 (general dental guidance score ~0.8) with PLAN-003 weakly present (score <0.1)
  - **All placeholder chunks score <0.1 across test queries**

---

#### Step 5: Implement Status Filtering (Day 5)
- **Action:**
  - Include chunks with status=[Approved, Active, Needs Review, Pending Detail]
  - **EXCLUDE chunks with status=Deprecated** (delete from index or filter at query time)
- **Validation:**
  - If any Deprecated chunks exist in source files, confirm NOT retrieved
  - Status filter working correctly

**End Week 1 Checkpoint:**
- ✅ All 87 chunks ingested (67 strong + 20 placeholders)
- ✅ Semantic search working
- ✅ Placeholder downweighting working (all scores <0.1)
- ✅ Status filtering working
- ✅ Ready for retrieval flow implementation

---

### Priority 2: Retrieval Flow and Safety Rules (Week 2-3)

#### Step 6: Implement 8-Step Retrieval Flow (Day 6-8)
**Reference:** PROTOTYPE_RETRIEVAL_FLOW.md

**Implement each step:**
1. **Query Normalization:** Lowercase, extract entities (plan names, provider names), identify intent
2. **FAQ Retrieval:** Retrieve top 3-5 FAQ chunks, filter status=[Approved,Active], boost weight ×1.0
3. **Rules Retrieval:** Retrieve top 2-4 Rules chunks, cross-link to FAQ
4. **Mapping Retrieval:** Retrieve top 1-3 Mapping chunks for context (never display directly)
5. **Placeholder Context:** If plan/network query, retrieve top 1-2 placeholders with penalty ×0.08 (recognize names only, NEVER as truth)
6. **Source Assembly:** Combine, sort, group by chunk_type, calculate confidence tier using weakest link rule: `overall_confidence = MIN(confidence of all chunks)`
7. **Answer Generation:** Generate answer by confidence tier, apply safety rules, add disclaimers
8. **Traceability Attachment:** Attach full metadata (sources, confidence tier, disclaimers, safety rules triggered, performance metrics)

**Validation:**
- Run test query "What is a deductible?" → Tier 1 answer from FAQ-001, no disclaimers
- Run test query "Does Basic Family Plan cover dental?" → Tier 3 answer from FAQ-005, recognizes plan name, mandatory disclaimer, NO placeholder details stated

---

#### Step 7: Implement Confidence Tier Logic (Day 8-9)
**Reference:** PROTOTYPE_RETRIEVAL_FLOW.md Section "Confidence Tiers"

**Implement 5 tiers:**
- **Tier 1 (Strongest):** FAQ + Rules only, no placeholders → Confident answer, minimal disclaimers
- **Tier 2 (Strong):** + Mapping support → Strong answer with cross-references
- **Tier 3 (Moderate):** + Placeholders present → Cautious answer, mandatory disclaimers
- **Tier 4 (Weak):** Rules-only or low semantic match → Weak answer, caution disclaimers
- **Tier 5 (Unsafe):** Placeholders-only or no reliable sources → Fallback, refuse certainty

**Implement weakest link rule:**
```python
# Pseudocode
def calculate_confidence_tier(retrieved_chunks):
    has_faq = any(chunk.chunk_type == "FAQ" for chunk in retrieved_chunks)
    has_rules = any(chunk.chunk_type == "Rules" for chunk in retrieved_chunks)
    has_placeholder = any(chunk.is_placeholder == True for chunk in retrieved_chunks)
    max_semantic_score = max(chunk.semantic_score for chunk in retrieved_chunks)
    
    # Tier 5: Placeholder-only or no reliable sources
    if (has_placeholder and not has_faq and not has_rules) or max_semantic_score < 0.5:
        return "Tier 5"
    
    # Tier 4: Rules-only or low confidence
    if has_rules and not has_faq and max_semantic_score < 0.7:
        return "Tier 4"
    
    # Tier 3: Placeholders present (even if FAQ/Rules also present)
    if has_placeholder:
        return "Tier 3"
    
    # Tier 2: FAQ + Rules + Mapping (no placeholders)
    if has_faq and has_rules:
        return "Tier 2"
    
    # Tier 1: FAQ + Rules only (strongest)
    if has_faq and has_rules:
        return "Tier 1"
    
    # Default: Tier 4 (weak)
    return "Tier 4"
```

**Validation:**
- Conceptual query "What is deductible?" → Tier 1
- Plan-specific query "Does Basic Family Plan cover dental?" → Tier 3 (placeholder present)
- Account-specific query "What's my claim status?" → Tier 5 (no reliable sources)

---

#### Step 8: Implement Mandatory Disclaimers (Day 9-10)
**Reference:** PROTOTYPE_RESPONSE_BEHAVIOR.md Section "Disclaimer Application Rules"

**Implement 6 mandatory situations:**

```python
# Pseudocode
def determine_disclaimers(query, retrieved_chunks, confidence_tier):
    disclaimers = []
    
    # 1. Plan confirmation disclaimer
    if requires_plan_confirmation(query, retrieved_chunks):
        disclaimers.append("Coverage details vary by plan. Check your policy documents or contact customer service.")
    
    # 2. Network verification disclaimer
    if requires_network_verification(query, retrieved_chunks):
        disclaimers.append("Provider network status may vary. Always verify with customer service before scheduling your appointment.")
    
    # 3. Operational pending disclaimer
    if any(chunk.chunk_type == "FAQ" and chunk.status == "Pending Detail" for chunk in retrieved_chunks):
        disclaimers.append("For complete step-by-step instructions, contact customer service.")
    
    # 4. Placeholder present disclaimer
    if confidence_tier == "Tier 3" or any(chunk.is_placeholder for chunk in retrieved_chunks):
        disclaimers.append("For plan-specific details, check your policy documents or contact customer service at [number].")
    
    # 5. Low confidence disclaimer
    if max(chunk.semantic_score for chunk in retrieved_chunks) < 0.6:
        disclaimers.append("This guidance is general. For personalized assistance, contact customer service.")
    
    # 6. Compliance/legal disclaimer
    if any(chunk.chunk_type == "Rules" and chunk.status == "Needs Review" and is_compliance_topic(query) for chunk in retrieved_chunks):
        disclaimers.append("This is a compliance matter. For personalized guidance, contact the compliance team or benefits advisor.")
    
    return disclaimers

def requires_plan_confirmation(query, chunks):
    # Returns True if query mentions plan names OR any Plans placeholder retrieved
    plan_names = ["Basic Family Plan", "Premium Individual Plan", "Economy Plan", "Starter Plan", "Corporate Group Plan"]
    has_plan_name = any(name.lower() in query.lower() for name in plan_names)
    has_plan_chunk = any(chunk.chunk_type == "Plans" for chunk in chunks)
    return has_plan_name or has_plan_chunk

def requires_network_verification(query, chunks):
    # Returns True if query mentions providers/facilities OR any Network placeholder retrieved
    network_keywords = ["in-network", "out-of-network", "provider", "doctor", "Dr.", "hospital", "clinic", "facility"]
    has_network_keyword = any(keyword.lower() in query.lower() for keyword in network_keywords)
    has_network_chunk = any(chunk.chunk_type == "Network" for chunk in chunks)
    return has_network_keyword or has_network_chunk
```

**Validation:**
- Query "Does Basic Family Plan cover dental?" → **MUST include plan confirmation disclaimer**
- Query "Is Dr. Ahmed in-network?" → **MUST include network verification disclaimer**
- Query "What is deductible?" (Tier 1, FAQ-only, high confidence) → NO disclaimers

---

#### Step 9: Implement Exclusion Detection (Day 10-11)
**Reference:** PROTOTYPE_EXCLUSIONS.md

**Implement CRITICAL exclusion detection:**

```python
# Pseudocode
def detect_exclusion_violations(query, answer_draft, retrieved_chunks):
    violations = []
    
    # CRITICAL: Exclusion 1 - Plan Benefit Claims
    if placeholder_benefit_stated_as_fact(answer_draft, retrieved_chunks):
        violations.append({
            "exclusion": 1,
            "severity": "CRITICAL",
            "description": "Placeholder plan benefit stated as fact",
            "action": "BLOCK answer, generate safe fallback"
        })
    
    # CRITICAL: Exclusion 2 - Network Status Confirmation
    if network_status_confirmed_from_placeholder(answer_draft, retrieved_chunks):
        violations.append({
            "exclusion": 2,
            "severity": "CRITICAL",
            "description": "Network status confirmed from placeholder",
            "action": "BLOCK answer, generate verification process response"
        })
    
    # CRITICAL: Exclusion 3 - Cost/Pricing Claims
    if specific_cost_from_placeholder(answer_draft, retrieved_chunks):
        violations.append({
            "exclusion": 3,
            "severity": "CRITICAL",
            "description": "Specific cost stated from placeholder",
            "action": "BLOCK answer, generate cost concept response with verification"
        })
    
    # HIGH: Exclusion 4 - Claims Adjudication
    if claims_adjudication_attempted(query, answer_draft):
        violations.append({
            "exclusion": 4,
            "severity": "HIGH",
            "description": "Claims adjudication attempted",
            "action": "BLOCK answer, direct to claims department"
        })
    
    # Additional exclusions 5-9...
    
    return violations

def placeholder_benefit_stated_as_fact(answer, chunks):
    # Returns True if answer states placeholder benefit details as confirmed facts
    has_placeholder = any(chunk.is_placeholder and chunk.chunk_type == "Plans" for chunk in chunks)
    if not has_placeholder:
        return False
    
    # Check for prohibited patterns:
    # "Basic Family Plan covers [benefit] with [percentage]"
    # "Premium Plan includes [benefit]"
    # "Economy Plan does not include [benefit]"
    prohibited_patterns = [
        r"(Basic Family Plan|Premium Individual Plan|Economy Plan|Starter Plan) covers? .+ with \d+%",
        r"(Basic Family Plan|Premium Individual Plan|Economy Plan|Starter Plan) includes? .+",
        r"(Basic Family Plan|Premium Individual Plan|Economy Plan|Starter Plan) does not include .+",
    ]
    
    for pattern in prohibited_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            return True
    
    return False
```

**Validation:**
- If answer states "Basic Family Plan covers dental with 80% coinsurance" → **VIOLATION DETECTED, answer BLOCKED**
- If answer states "For your Basic Family Plan's specific dental coverage, check your policy documents" → **ALLOWED (recognizes name, provides verification)**

---

#### Step 10: Implement Traceability Metadata (Day 11-12)
**Reference:** PROTOTYPE_RESPONSE_BEHAVIOR.md Section "Traceability Requirements"

**For each answer, attach full metadata:**

```json
{
  "query_metadata": {
    "query_text": "Does Basic Family Plan cover dental?",
    "query_timestamp": "2026-03-20T14:35:22Z",
    "query_classification": "Plan-Specific",
    "entities_extracted": ["Basic Family Plan", "dental"],
    "intent": "plan_benefit_inquiry"
  },
  "source_metadata": [
    {
      "chunk_id": "FAQ-005",
      "chunk_type": "FAQ",
      "status": "Approved",
      "confidence": "High",
      "retrieval_score": 0.87,
      "retrieval_rank": 1,
      "safe_for_client_direct_use": true,
      "is_placeholder": false
    },
    {
      "chunk_id": "PLAN-003",
      "chunk_type": "Plans",
      "status": "Pending Detail",
      "confidence": "Low",
      "retrieval_score": 0.07,
      "retrieval_rank": 5,
      "safe_for_client_direct_use": false,
      "is_placeholder": true
    }
  ],
  "answer_metadata": {
    "overall_confidence_tier": "Tier 3",
    "weakest_source": {
      "chunk_id": "PLAN-003",
      "reason": "Placeholder chunk present"
    },
    "disclaimers_applied": [
      "Coverage details vary by plan. Check your policy documents or contact customer service."
    ],
    "safety_rules_triggered": [
      "plan_confirmation_required",
      "placeholder_present"
    ],
    "exclusions_checked": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "violations_detected": []
  },
  "performance_metadata": {
    "retrieval_latency_ms": 145,
    "answer_generation_time_ms": 65,
    "total_time_ms": 210,
    "chunks_retrieved_total": 8,
    "chunks_by_type": {
      "FAQ": 3,
      "Rules": 2,
      "Mapping": 1,
      "Plans": 2,
      "Network": 0
    }
  }
}
```

**Validation:**
- All metadata fields present
- Can trace answer back to source chunks
- Can verify confidence tier calculation
- Can audit disclaimer application
- Can measure performance

---

### Priority 3: Testing and Validation (Week 2-3)

#### Step 11: Run Core Test Queries (Day 13-15)
**Reference:** PROTOTYPE_TEST_QUERIES.md, INTERNAL_TESTING_PLAN.md

**Execute all 30 test queries:**
- Record results using test results template
- Validate against success criteria
- **CRITICAL:** ALL plan-specific queries (3.1-3.5) must have mandatory disclaimers and NO placeholder details stated
- **CRITICAL:** ALL network-specific queries (4.1-4.2) must have verification disclaimers and NO network status confirmed
- Document any violations (DEPLOYMENT BLOCKERS)

---

#### Step 12: Safety Violation Testing (Day 15-16)
**Reference:** INTERNAL_TESTING_PLAN.md Section "Test Set 3"

**Attempt to trigger violations:**
- Placeholder leakage attempts
- Network confirmation attempts
- Cost statement attempts
- Inappropriate operations attempts

**Expected result:** **0 successful violations** (all blocked by safety rules)

**If ANY violations successful:** **STOP, fix immediately, retest**

---

#### Step 13: Compile Test Results and GO/NO-GO (Day 17-18)
**Reference:** PROTOTYPE_SUCCESS_CRITERIA.md

**Calculate metrics against targets:**
- FAQ retrieval relevance (target ≥85%)
- Rules retrieval relevance (target ≥80%)
- Answer relevance (target ≥80%)
- **Placeholder leak rate (target 0%)**
- **Mandatory disclaimer firing (target 100%)**
- **No inappropriate operations (target 0%)**
- Source metadata completeness (target 100%)
- Answer metadata completeness (target 100%)

**Make GO/NO-GO decision:**
- **GO:** ALL 6 CRITICAL requirements pass + ≥4 of 6 HIGH requirements pass
- **NO-GO:** ANY CRITICAL failure OR <3 HIGH requirements pass → Fix and retest

---

## What Safeguards Are Mandatory

### MANDATORY Safeguard 1: Placeholder Downweighting

**Implementation:**
```python
# Apply penalty to all placeholder chunks BEFORE ranking
for chunk in retrieved_chunks:
    if chunk.is_placeholder:
        chunk.final_score = chunk.semantic_score * chunk.retrieval_weight * PLACEHOLDER_PENALTY
        # PLACEHOLDER_PENALTY = 0.08

# Expected: All placeholder chunks score <0.1 after penalty
```

**Validation:**
- Test query "What is deductible?" → PLAN-003 placeholder score <0.1
- Test query "Does Basic Family Plan cover dental?" → PLAN-003 placeholder score <0.1 (ranked low)
- **If ANY placeholder scores ≥0.1 → CRITICAL FAILURE**

---

### MANDATORY Safeguard 2: is_placeholder Filtering for Customer-Facing Use

**Implementation:**
```python
# For any answer that might be shown to customers (Phase 6+):
def filter_for_customer_use(chunks):
    return [chunk for chunk in chunks if chunk.safe_for_client_direct_use == True]

# For Phase 1 internal testing, allow placeholders but with strict guardrails
def allow_placeholders_with_guardrails(chunks):
    # Placeholders allowed for context (recognize names)
    # BUT never state details as facts
    # AND mandatory disclaimers added
    return chunks  # All chunks, but answer generation enforces rules
```

**Validation:**
- Phase 1: Placeholders retrieved but NEVER stated as facts
- Phase 2+: Before customer-facing, confirm only safe_for_client_direct_use=TRUE chunks used

---

### MANDATORY Safeguard 3: Mandatory Disclaimer Firing

**Implementation:**
- Implement disclaimer logic from Step 8
- **MUST fire for:**
  - Plan-specific queries (any plan name mentioned OR Plans chunk retrieved)
  - Network-specific queries (any network keyword OR Network chunk retrieved)
  - Tier 3 queries (placeholders present)
  - Compliance/legal topics
  - Low confidence (<0.6 semantic match)
  - Operational pending (FAQ status=Pending Detail)

**Validation:**
- Test query "Does Basic Family Plan cover dental?" → **MUST include plan disclaimer**
- Test query "Is Dr. Ahmed in-network?" → **MUST include network verification disclaimer**
- **If ANY required disclaimer missing → CRITICAL FAILURE**

---

### MANDATORY Safeguard 4: Weakest Link Confidence Rule

**Implementation:**
```python
# Overall confidence = MIN of all source confidences
def calculate_confidence_tier(chunks):
    # If ANY placeholder present → Tier 3 (or lower)
    if any(chunk.is_placeholder for chunk in chunks):
        return max("Tier 3", calculate_base_tier(chunks))
    
    # If ANY source is weak → downgrade overall tier
    # Confidence is weakest link, not average
    return calculate_base_tier(chunks)
```

**Validation:**
- Query with FAQ (High) + Rules (High) → Tier 1
- Query with FAQ (High) + Rules (High) + Placeholder (Low) → Tier 3 (downgrade due to placeholder)
- Query with only Placeholder (Low) → Tier 5 (unsafe fallback)

---

### MANDATORY Safeguard 5: Exclusion Violation Detection

**Implementation:**
- Implement exclusion detection from Step 9
- **MUST detect and block:**
  - Exclusion 1: Placeholder plan benefits stated as facts (CRITICAL)
  - Exclusion 2: Network status confirmed from placeholder (CRITICAL)
  - Exclusion 3: Specific costs from placeholder (CRITICAL)
  - Exclusion 4: Claims adjudication attempted (HIGH)
  - Exclusion 5: Underwriting decisions attempted (HIGH)
  - Exclusions 6-9: Legal, medical, account, policy replacement (HIGH/MEDIUM)

**Validation:**
- Safety violation testing (Step 12) must show 0 successful violations
- **If ANY violations detected → CRITICAL FAILURE, STOP, fix immediately**

---

### MANDATORY Safeguard 6: Full Traceability Metadata

**Implementation:**
- Attach full metadata from Step 10 to every answer
- **MUST include:**
  - All source chunks (chunk_id, type, status, scores)
  - Confidence tier calculation
  - Disclaimers applied
  - Safety rules triggered
  - Exclusion checks performed
  - Violations detected (if any)
  - Performance metrics

**Validation:**
- All metadata fields present for all test queries
- Can audit ANY answer to verify safety compliance
- **If metadata missing → CRITICAL FAILURE (cannot audit)**

---

## What Should Remain Disabled

### Disabled Feature 1: Customer-Facing Deployment

**Status:** **DISABLED for Phase 1**

**Why:**
- Placeholder Plans/Network data not real
- Safety rules not production-validated
- Retrieval quality not customer-tested
- Legal/compliance review not complete

**When to Enable:**
- **Phase 6+:** After real plan data (Phase 2), real network data (Phase 3), advanced retrieval (Phase 4), LLM answer generation (Phase 5), pilot testing, compliance review

---

### Disabled Feature 2: Direct Plan Benefit Confirmation from Placeholders

**Status:** **DISABLED for Phase 1, 2, 3, ... until real data ingested**

**Implementation:**
```python
# BLOCKED behavior:
# ❌ "Yes, Basic Family Plan covers dental with 80% coinsurance."

# ALLOWED behavior:
# ✅ "Dental coverage varies by plan. For your Basic Family Plan's specific dental coverage, check your policy documents."

def answer_plan_benefit_query(query, chunks):
    has_placeholder = any(chunk.is_placeholder and chunk.chunk_type == "Plans" for chunk in chunks)
    
    if has_placeholder:
        # DO NOT state placeholder details as facts
        # DO provide general guidance from FAQ/Rules
        # DO recognize plan name for context
        # DO add mandatory disclaimer
        return generate_general_guidance_with_disclaimer(query, chunks)
    else:
        # No plan-specific info available
        return generate_general_guidance(query, chunks)
```

**When to Enable:**
- **Phase 2+:** After real plan data ingested and validated

---

### Disabled Feature 3: Live Network Status Confirmation from Placeholders

**Status:** **DISABLED for Phase 1, 2, ... until real network data ingested**

**Implementation:**
```python
# BLOCKED behavior:
# ❌ "Yes, Dr. Ahmed is in-network."

# ALLOWED behavior:
# ✅ "To verify if Dr. Ahmed is in your network, call customer service at [number]."

def answer_network_query(query, chunks):
    has_network_placeholder = any(chunk.is_placeholder and chunk.chunk_type == "Network" for chunk in chunks)
    
    if has_network_placeholder:
        # DO NOT confirm network status from placeholder
        # DO provide verification process from FAQ
        # DO recognize provider/facility name for context
        # DO add mandatory verification disclaimer
        return generate_verification_process_with_disclaimer(query, chunks)
    else:
        # Provide general network guidance
        return generate_network_guidance(query, chunks)
```

**When to Enable:**
- **Phase 3+:** After real network data ingested and provider directory integrated

---

### Disabled Feature 4: Cost/Pricing from Placeholders

**Status:** **DISABLED until real plan data**

**Implementation:**
```python
# BLOCKED: Specific dollar amounts from placeholders
# ALLOWED: General cost concepts and typical ranges

def answer_cost_query(query, chunks):
    # DO NOT state specific costs from placeholders
    # DO explain cost-sharing concepts generally
    # DO provide typical ranges if available in FAQ
    # DO direct to customer service for plan-specific pricing
    return generate_cost_concept_response_with_verification(query, chunks)
```

**When to Enable:**
- **Phase 2+:** After real plan cost data ingested

---

### Disabled Feature 5: Claims Adjudication and Account Operations

**Status:** **DISABLED for Phase 1** (no system integrations)

**Implementation:**
```python
# BLOCKED: Claims approval/denial, account operations
# ALLOWED: Process guidance

def answer_account_query(query):
    if is_account_specific(query):
        # Tier 5 fallback
        return "For account-specific information, log into your member portal or contact customer service."
    else:
        # Provide process guidance if available
        return generate_process_guidance(query)
```

**When to Enable:**
- **Phase 5+:** After read-only integration with claims/account systems (internal users only)
- **Production:** Full integration with authentication and authorization

---

### Disabled Feature 6: LLM Answer Generation (Optional for Phase 1)

**Status:** **OPTIONAL for Phase 1**

**Implementation:**
- Phase 1 can use template-based or chunk-concatenation answers
- LLM answer generation (GPT-4, Claude, etc.) optional
- If LLM used, MUST still enforce safety rules, disclaimers, exclusions

**When to Enable:**
- **Phase 5+:** LLM-based answer generation with prompt engineering and safety guardrails

---

## What Evidence to Provide Before Phase 2

### Evidence 1: Test Results Summary

**Required:**
- Test results for all 30 core test queries (PROTOTYPE_TEST_QUERIES.md)
- Success metrics calculated:
  - FAQ retrieval relevance: __%
  - Rules retrieval relevance: __%
  - Answer relevance: __%
  - **Placeholder leak rate: 0%** ✅
  - **Mandatory disclaimer firing: 100%** ✅
  - **No inappropriate operations: 0%** ✅
  - Source metadata completeness: 100% ✅
  - Answer metadata completeness: 100% ✅
- Safety violation testing results: **0 successful violations** ✅
- GO/NO-GO decision: **GO** ✅

**Format:** Final test report per INTERNAL_TESTING_PLAN.md

---

### Evidence 2: Safety Compliance Certificate

**Required:**
- Confirmation that ALL 6 CRITICAL requirements passed:
  1. ✅ Zero placeholder leakage = 0%
  2. ✅ Mandatory disclaimers firing = 100%
  3. ✅ Placeholder downweighting < 0.1 all queries
  4. ✅ Source metadata completeness = 100%
  5. ✅ Answer metadata completeness = 100%
  6. ✅ No inappropriate operations = 0%
- Example test cases demonstrating safety enforcement:
  - Query 3.1: Plan-specific query with mandatory disclaimer, NO placeholder details
  - Query 4.1: Network-specific query with verification disclaimer, NO network confirmation
  - Safety violation attempt BLOCKED successfully
- Sign-off from compliance team: Internal testing approved

---

### Evidence 3: KB Quality Assessment

**Required:**
- List of ≥5 KB improvement opportunities identified
- For each gap:
  - Gap type (missing FAQ, incomplete FAQ, missing Rules, inconsistent wording, missing cross-reference)
  - Query that revealed gap
  - Current KB state
  - Suggested improvement
  - Priority (High/Medium/Low)
- KB improvement plan for Phase 2

**Format:** KB Quality Assessment Report per INTERNAL_TESTING_PLAN.md

---

### Evidence 4: Performance Baseline

**Required:**
- Performance metrics measured:
  - Average retrieval latency: ___ ms
  - P95 retrieval latency: ___ ms
  - Average total time (retrieval + answer generation): ___ ms
  - Chunks retrieved per query (avg): ___
- Infrastructure details:
  - Embedding model used: ___
  - Vector database used: ___
  - RAG framework used: ___
  - Deployment environment: ___
- Cost estimate per query: $___

**Purpose:** Baseline for Phase 2+ optimization

---

### Evidence 5: Stakeholder Sign-Off

**Required:**
- **Product Team:** Confirms scope appropriate for internal testing, Phase 2 priorities identified
- **Compliance Team:** Approves safety rules for internal use, identifies requirements for customer-facing deployment
- **Knowledge Team:** Confirms test queries representative, KB quality gaps identified
- **Engineering Team:** Confirms spec implementable, traceability working, ready for Phase 2 enhancements

**Format:** Sign-off document with signatures/approvals

---

### Evidence 6: Lessons Learned and Phase 2 Plan

**Required:**
- **Lessons Learned:**
  - What worked well in Phase 1
  - What was challenging
  - What would we do differently
  - Surprises or unexpected findings
- **Phase 2 Plan:**
  - Real plan data ingestion approach
  - Data sources for real plan data
  - Timeline for Phase 2 (estimated 6 months)
  - Success criteria for Phase 2
  - Resource requirements

**Purpose:** Inform Phase 2 planning and continuous improvement

---

## Implementation Checklist

### Before You Start
- [ ] Read all specification documents (PROTOTYPE_OVERVIEW.md through HANDOFF_TO_ENGINEERING.md)
- [ ] Understand scope: Internal testing only, NOT customer-facing
- [ ] Understand critical requirement: **Zero placeholder leakage**
- [ ] Choose technology stack (embedding model, vector DB, RAG framework)
- [ ] Set up development environment

### Week 1: Core Retrieval
- [ ] Step 1: Ingest FAQ chunks (20 chunks)
- [ ] Step 2: Ingest Rules chunks (27 chunks)
- [ ] Step 3: Ingest Mapping chunks (20 chunks)
- [ ] Step 4: Apply placeholder penalties (10 Plans + 10 Network, all score <0.1)
- [ ] Step 5: Implement status filtering (exclude Deprecated)
- [ ] Validate: All 87 chunks indexed, placeholder downweighting working

### Week 2: Retrieval Flow and Safety
- [ ] Step 6: Implement 8-step retrieval flow
- [ ] Step 7: Implement confidence tier logic (Tier 1-5, weakest link rule)
- [ ] Step 8: Implement mandatory disclaimers (6 situations)
- [ ] Step 9: Implement exclusion detection (9 exclusions, CRITICAL blocking)
- [ ] Step 10: Implement traceability metadata (full source/answer/performance metadata)
- [ ] Validate: Retrieval flow working, safety rules enforced, traceability complete

### Week 2-3: Testing
- [ ] Step 11: Run core test queries (30 queries, record results)
- [ ] Step 12: Safety violation testing (0 successful violations)
- [ ] Step 13: Compile test results, calculate metrics, GO/NO-GO decision
- [ ] Fix any CRITICAL failures immediately
- [ ] Iterate on HIGH/MEDIUM issues if time allows

### Before Phase 2
- [ ] Evidence 1: Test results summary with GO decision
- [ ] Evidence 2: Safety compliance certificate
- [ ] Evidence 3: KB quality assessment (≥5 gaps identified)
- [ ] Evidence 4: Performance baseline measured
- [ ] Evidence 5: Stakeholder sign-off (product, compliance, knowledge, engineering)
- [ ] Evidence 6: Lessons learned and Phase 2 plan

---

## Quick Reference: Critical Requirements

**YOU MUST:**
1. ✅ Downweight ALL placeholder chunks (×0.08, final score <0.1)
2. ✅ Fire mandatory disclaimers (plan confirmation, network verification, placeholder present, low confidence, compliance, operational pending)
3. ✅ Block placeholder details from being stated as facts (CRITICAL violations)
4. ✅ Implement weakest link confidence rule (Tier 3 or lower if placeholders present)
5. ✅ Attach full traceability metadata to every answer
6. ✅ Achieve 0% placeholder leak rate across test queries

**YOU MUST NOT:**
1. ❌ Allow ANY placeholder plan benefits, network status, or costs to be stated as confirmed facts
2. ❌ Skip mandatory disclaimers for plan/network queries
3. ❌ Deploy customer-facing (Phase 1 is internal testing only)
4. ❌ Attempt claims adjudication, underwriting decisions, or account operations
5. ❌ Proceed to Phase 2 without passing ALL 6 CRITICAL requirements

---

## Support and Questions

**For questions about:**
- **Specification interpretation:** Review related specification documents (cross-references provided)
- **Safety requirements:** PROTOTYPE_EXCLUSIONS.md, PROTOTYPE_RESPONSE_BEHAVIOR.md
- **Testing approach:** INTERNAL_TESTING_PLAN.md, PROTOTYPE_TEST_QUERIES.md
- **Success criteria:** PROTOTYPE_SUCCESS_CRITERIA.md
- **Scope boundaries:** PROTOTYPE_SCOPE.md, PROTOTYPE_LIMITATIONS.md

**If unclear:**
- Prefer conservative behavior (reject uncertain rather than overstate)
- When in doubt, add disclaimer
- Always preserve traceability
- Never state placeholder details as facts

---

## Document Control

**Filename:** HANDOFF_TO_ENGINEERING.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_RETRIEVAL_FLOW.md - Detailed retrieval flow
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Answer generation rules
- PROTOTYPE_EXCLUSIONS.md - Safety boundaries
- PROTOTYPE_TEST_QUERIES.md - Test query set
- PROTOTYPE_SUCCESS_CRITERIA.md - Success metrics
- INTERNAL_TESTING_PLAN.md - Testing approach
- PROTOTYPE_LIMITATIONS.md - Current limitations

---

**END OF ENGINEERING HANDOFF**

**Good luck with implementation! Remember: Truth over completeness, safety over features.**
