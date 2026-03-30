# Implementation Phases Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define stepwise rollout plan for RAG implementation

---

## 1. Overview

This specification defines **5 implementation phases** (A through E) for safe, incremental deployment of the Micro Insurance Knowledge Base RAG system.

### Phased Rollout Strategy

**Why Phased:**
- Reduce risk of widespread failures
- Allow testing and validation at each stage
- Enable rollback to previous phase if issues detected
- Build confidence gradually from internal to production

**Phase Progression:**
```
Phase A: Metadata-Ready Intake
  ↓ (Validation gate)
Phase B: FAQ+Rules+Mapping Retrieval Only
  ↓ (Internal testing gate)
Phase C: Placeholder-Aware with Guardrails
  ↓ (Limited pilot gate)
Phase D: Real Data Replacement and Re-Index
  ↓ (Full production gate)
Phase E: Production Hardening and Optimization
```

---

## 2. Phase A: Metadata-Ready Intake

### Goal
Prepare KB_PACK_V1 for ingestion with all metadata correctly applied and validated

### Scope
**IN SCOPE:**
- Read all 5 JSONL files (faq_chunks.jsonl, rules_chunks.jsonl, plans_chunks.jsonl, network_chunks.jsonl, mapping_reference.jsonl)
- Apply metadata derivation rules (from METADATA_APPLICATION_SPEC.md)
- Validate metadata completeness and correctness
- Create metadata-enriched chunks ready for embedding

**OUT OF SCOPE:**
- Embedding generation (next phase)
- Vector database indexing (next phase)
- Retrieval testing (next phase)

### Prerequisites
- ✅ KB_PACK_V1 available (87 chunks in 5 JSONL files)
- ✅ RAG_EXECUTION_SPEC_V1 approved
- ✅ Technology stack chosen (embedding model, vector DB, RAG framework)
- ✅ Development environment configured

### Inputs
- `data/faq_chunks.jsonl` (20 chunks)
- `data/rules_chunks.jsonl` (27 chunks)
- `data/plans_chunks.jsonl` (10 chunks)
- `data/network_chunks.jsonl` (10 chunks)
- `data/mapping_reference.jsonl` (20 chunks)
- METADATA_APPLICATION_SPEC.md (derivation rules)

### Process Steps

**Step 1: Parse JSONL files**
```python
chunks = []
for file in ['faq_chunks.jsonl', 'rules_chunks.jsonl', ...]:
    with open(file) as f:
        for line in f:
            chunks.append(json.loads(line))
```

**Step 2: Apply metadata derivation rules**
```python
for chunk in chunks:
    # Apply Rule 1: Core fields
    chunk['chunk_id'] = derive_chunk_id(chunk)
    chunk['chunk_type'] = derive_chunk_type(chunk)
    
    # Apply Rule 2: CRITICAL safety fields
    chunk['is_placeholder'] = derive_is_placeholder(chunk)
    chunk['safe_for_client_direct_use'] = derive_safe_for_client(chunk)
    chunk['requires_plan_confirmation'] = derive_requires_plan(chunk)
    chunk['requires_network_verification'] = derive_requires_network(chunk)
    
    # Apply Rule 3: Retrieval fields
    chunk['retrieval_weight_hint'] = derive_weight(chunk)
    chunk['ingestion_priority'] = derive_priority(chunk)
    chunk['confidence'] = derive_confidence(chunk)
    
    # Apply Rules 4-9: Other metadata...
```

**Step 3: Validate metadata completeness**
```python
for chunk in chunks:
    validate_core_fields(chunk)
    validate_safety_fields(chunk)
    validate_retrieval_fields(chunk)
    validate_cross_field_consistency(chunk)
```

**Step 4: Generate metadata-enriched output**
- Save validated chunks with full metadata
- Ready for Phase B ingestion

### Outputs
- 87 metadata-enriched chunks (validated)
- Metadata validation report (100% pass required)
- Chunk statistics summary (counts by type, status, is_placeholder)

### Success Criteria
- ✅ All 87 chunks parsed successfully
- ✅ All required metadata fields present
- ✅ All Plans chunks (10) have `is_placeholder: true`
- ✅ All Network chunks (10) have `is_placeholder: true`
- ✅ All FAQ/Rules/Mapping chunks (67) have `is_placeholder: false`
- ✅ All placeholders have `safe_for_client_direct_use: false`
- ✅ Retrieval weights in valid range (0.0-1.0)
- ✅ Cross-field consistency validated
- ✅ Metadata validation report shows 0 errors

### Risks and Mitigations

**Risk 1: Metadata derivation errors**
- **Impact:** Incorrect safety flags → placeholder leaks
- **Mitigation:** Automated validation checks, manual spot-check of 10%
- **Rollback:** Fix derivation logic, re-run Phase A

**Risk 2: Missing metadata fields**
- **Impact:** Deployment blocked
- **Mitigation:** Schema validation, required fields check
- **Rollback:** Complete metadata application, re-validate

**Risk 3: Cross-field inconsistencies**
- **Impact:** Confusing retrieval behavior
- **Mitigation:** Cross-field validation rules (if is_placeholder=true then safe_for_client_direct_use=false)
- **Rollback:** Fix inconsistencies, re-validate

### Validation Gate
**Go/No-Go Criteria for Phase B:**
- ✅ Metadata validation report: 0 errors
- ✅ All safety-critical fields correct (is_placeholder, safe_for_client_direct_use)
- ✅ Spot-check 10% of chunks manually: 100% correct

**If NO-GO:** Fix errors, re-run Phase A, re-validate

### Timeline
**Estimated Duration:** 2-3 days  
**Dependencies:** Technology stack chosen  
**Team:** Data engineers, QA engineers  

---

## 3. Phase B: FAQ+Rules+Mapping Retrieval Only

### Goal
Deploy strong knowledge layer (67 chunks) with retrieval testing, NO placeholders yet

### Scope
**IN SCOPE:**
- Ingest Phase 1 chunks only (FAQ 20 + Rules 27 + Mapping 20 = 67 chunks)
- Generate embeddings
- Index in vector database
- Implement retrieval logic with filtering/weighting
- Test retrieval quality
- Internal testing only (NOT customer-facing)

**OUT OF SCOPE:**
- Phase 2 placeholders (NOT ingested yet)
- Customer-facing deployment (internal only)
- Answer generation testing (retrieval focus)

### Prerequisites
- ✅ Phase A completed (metadata validated)
- ✅ Embedding model configured
- ✅ Vector database deployed
- ✅ Retrieval pipeline implemented

### Inputs
- 67 metadata-enriched chunks (FAQ + Rules + Mapping)
- Embedding model (chosen in technology stack)
- Vector database (configured)
- INGESTION_SEQUENCE.md (Phase 1 order)
- CHUNK_FILTERING_RULES.md (filtering logic)
- RETRIEVAL_WEIGHTING_SPEC.md (weighting formula)

### Process Steps

**Step 1: Ingest Phase 1 chunks in order**
```
1.1: FAQ chunks (20) - Approved → Needs Review → Pending Detail
1.2: Rules chunks (27) - Active → Needs Review
1.3: Mapping chunks (20) - High → Medium → Low confidence
```

**Step 2: Generate embeddings**
```python
for chunk in phase1_chunks:
    embedding = embedding_model.encode(chunk['text'])
    chunk['embedding'] = embedding
```

**Step 3: Index in vector database**
```python
for chunk in phase1_chunks:
    vector_db.insert(
        id=chunk['chunk_id'],
        vector=chunk['embedding'],
        metadata=chunk  # All metadata fields
    )
```

**Step 4: Test retrieval**
- Run 50 sample queries
- Review top-10 results for each query
- Validate chunk type distribution (FAQ/Rules dominant)
- Validate weighting (FAQ Approved scores higher than FAQ Pending Detail)

### Outputs
- 67 chunks indexed in vector database
- Retrieval test results (50 queries × top-10 chunks)
- Chunk type distribution report
- Weight effectiveness report

### Success Criteria
- ✅ All 67 chunks indexed successfully
- ✅ FAQ retrieval relevance >85% (FAQ chunks in top-10 for FAQ-related queries)
- ✅ Rules provide reasoning enrichment (Rules appear in top-10 alongside FAQ)
- ✅ Mapping cross-references functional (Mapping used to find related chunks)
- ✅ NO placeholders indexed yet (sanity check)
- ✅ Retrieval weight hierarchy maintained (FAQ Approved > FAQ Needs Review > FAQ Pending Detail)

### Risks and Mitigations

**Risk 1: Low FAQ retrieval relevance**
- **Impact:** Wrong answers retrieved
- **Mitigation:** Embedding model tuning, FAQ text quality review
- **Rollback:** Adjust embedding model, re-embed, re-index

**Risk 2: Rules not enriching FAQ**
- **Impact:** Answers lack policy reasoning
- **Mitigation:** Review Rules content, adjust weights
- **Rollback:** Increase Rules weights, re-test

**Risk 3: Mapping noise**
- **Impact:** Mapping displayed directly (confusing)
- **Mitigation:** Ensure mapping excluded from direct display in answer generation
- **Rollback:** Implement mapping display filter

### Validation Gate
**Go/No-Go Criteria for Phase C:**
- ✅ FAQ retrieval relevance >85%
- ✅ Rules enrichment functional
- ✅ Weight hierarchy maintained
- ✅ Internal testing feedback positive
- ✅ NO critical bugs

**If NO-GO:** Fix retrieval issues, re-test, re-validate

### Timeline
**Estimated Duration:** 1-2 weeks  
**Dependencies:** Phase A completed  
**Team:** Data engineers, ML engineers, QA engineers  

---

## 4. Phase C: Placeholder-Aware with Guardrails

### Goal
Add Plan/Network placeholders (20 chunks) with strict filtering and answer safety guardrails

### Scope
**IN SCOPE:**
- Ingest Phase 2 chunks (Plans 10 + Network 10 = 20 placeholders)
- Implement placeholder filtering (exclude from customer-facing)
- Implement answer safety behavior (disclaimers, fallbacks)
- Test placeholder detection and prevention
- Limited pilot (internal + small customer group)

**OUT OF SCOPE:**
- Full production deployment (limited pilot only)
- Real plan/network data (still placeholders)

### Prerequisites
- ✅ Phase B completed (67 chunks indexed, retrieval tested)
- ✅ Placeholder filtering implemented (from CHUNK_FILTERING_RULES.md)
- ✅ Answer safety behavior implemented (from ANSWER_SAFETY_BEHAVIOR.md)
- ✅ Placeholder enforcement checks implemented (from PLACEHOLDER_ENFORCEMENT_SPEC.md)

### Inputs
- 20 placeholder chunks (Plans + Network)
- Placeholder filtering logic
- Answer safety behavior logic
- PLACEHOLDER_ENFORCEMENT_SPEC.md (operational rules)
- ANSWER_SAFETY_BEHAVIOR.md (answer generation by scenario)

### Process Steps

**Step 1: Ingest Phase 2 chunks**
```
2.1: Plans placeholder chunks (10) - ALL with is_placeholder=true, weight=0.2
2.2: Network placeholder chunks (10) - ALL with is_placeholder=true, weight=0.2
```

**Step 2: Validate placeholder tagging**
```python
for chunk in phase2_chunks:
    assert chunk['is_placeholder'] == True
    assert chunk['safe_for_client_direct_use'] == False
    assert chunk['retrieval_weight_hint'] <= 0.3
```

**Step 3: Implement filtering**
```python
def retrieve_for_customer(query):
    filter = {"is_placeholder": False}  # Exclude placeholders
    results = vector_db.query(query, filter=filter, top_k=10)
    return results

def retrieve_for_internal(query):
    # No filtering, but label placeholders in results
    results = vector_db.query(query, top_k=10)
    for r in results:
        if r['is_placeholder']:
            r['label'] = "⚠️ PLACEHOLDER"
    return results
```

**Step 4: Test placeholder scenarios**
- Plan-specific query: "Does my Basic Family Plan cover dental?"
- Network query: "Is Dubai Medical Center in-network?"
- Validate placeholders downranked (not in top-10 for customer-facing)
- Validate disclaimers added

**Step 5: Limited pilot deployment**
- Internal users: Full access (see placeholders with warnings)
- Small customer group (10-20 customers): Customer-facing filtering (no placeholders)
- Monitor for placeholder leaks

### Outputs
- 87 total chunks indexed (67 + 20)
- Placeholder filtering test results
- Answer safety behavior test results
- Limited pilot feedback
- Placeholder leak monitoring report

### Success Criteria
- ✅ All 20 placeholders indexed with correct metadata
- ✅ Placeholder filter test passed (NO placeholders in customer-facing retrieval)
- ✅ Disclaimer test passed (plan/network questions get appropriate disclaimers)
- ✅ Placeholder leak rate 0% in pilot
- ✅ Limited pilot feedback positive
- ✅ NO critical bugs

### Risks and Mitigations

**Risk 1: Placeholder leak to customer answers**
- **Impact:** CRITICAL - Legal liability
- **Mitigation:** Pre-retrieval filtering, runtime guards, monitoring
- **Rollback:** Rollback to Phase B (remove Phase 2 chunks), fix filtering, re-deploy

**Risk 2: Excessive disclaimers (poor UX)**
- **Impact:** Customer frustration
- **Mitigation:** Review disclaimer language, balance safety and UX
- **Rollback:** Adjust disclaimer logic, re-test

**Risk 3: Placeholders rank too high (despite low weight)**
- **Impact:** Risk of placeholder appearance
- **Mitigation:** Decrease placeholder weights further (0.2 → 0.1)
- **Rollback:** Adjust weights, re-test, re-validate

### Validation Gate
**Go/No-Go Criteria for Phase D:**
- ✅ Placeholder leak rate 0% (no placeholders in customer answers)
- ✅ Answer safety behavior functional (correct disclaimers)
- ✅ Limited pilot feedback acceptable
- ✅ NO critical bugs
- ✅ Compliance approval obtained

**If NO-GO:** Fix issues, extend pilot, re-validate

### Timeline
**Estimated Duration:** 2-3 weeks  
**Dependencies:** Phase B completed  
**Team:** Data engineers, ML engineers, QA engineers, pilot customers  

---

## 5. Phase D: Real Data Replacement and Re-Index

### Goal
Replace Plan/Network placeholders with real product/provider data as it becomes available

### Scope
**IN SCOPE:**
- Obtain real Plan data (from product team)
- Obtain real Network data (from provider contracts team)
- Create new chunks with real data (is_placeholder=false, weight=0.9)
- Deprecate old placeholders (status=Deprecated, superseded_by link)
- Re-index with real data
- Update mappings
- Validate replacement

**OUT OF SCOPE:**
- Immediate removal of all placeholders (gradual replacement as data available)

### Prerequisites
- ✅ Phase C completed (placeholders with guardrails tested)
- ✅ Real Plan data available (from product finalization)
- ✅ Real Network data available (from provider contracts)
- ✅ Replacement process documented (from INGESTION_SEQUENCE.md Scenario B)

### Inputs
- Real Plan product documentation
- Real Network provider contracts
- Placeholder replacement process (INGESTION_SEQUENCE.md Scenario B)
- Mapping updates (link new chunks to FAQ/Rules)

### Process Steps

**Step 1: Create new chunk with real data**
```json
{
  "chunk_id": "PLAN-CHUNK-103",
  "plan_id": "PLAN-103",
  "plan_name": "Basic Family Plan",
  "text": "Basic Family Plan\nMonthly Premium: AED 550\nDeductible: AED 500\n...",
  "status": "Active",
  "is_placeholder": false,  ← Now real data
  "safe_for_client_direct_use": true,  ← Now safe
  "retrieval_weight_hint": 0.9,  ← Much higher
  "supersedes": "PLAN-003"
}
```

**Step 2: Deprecate old placeholder**
```json
{
  "chunk_id": "PLAN-CHUNK-003",
  "status": "Deprecated",
  "deprecated_date": "2026-09-15",
  "superseded_by": "PLAN-103"
}
```

**Step 3: Update mappings**
```json
{
  "chunk_id": "MAP-CHUNK-005",
  "related_plan_id": "PLAN-103"  ← Updated from PLAN-003
}
```

**Step 4: Remove old placeholder from retrieval**
- Filter out `status: "Deprecated"`
- Archive old placeholder (traceability, not active retrieval)

**Step 5: Validate replacement**
- Test queries mentioning "Basic Family Plan"
- Verify PLAN-103 retrieved (not PLAN-003)
- Verify answer provides real plan details
- Verify NO disclaimers needed (real data = high confidence)

### Outputs
- Real Plan chunks (up to 10 as data becomes available)
- Real Network chunks (up to 10 as data becomes available)
- Deprecated placeholder chunks (archived)
- Updated mappings
- Replacement validation report

### Success Criteria
- ✅ New real data chunks indexed correctly
- ✅ Old placeholders deprecated and removed from retrieval
- ✅ Mappings updated to reference new chunks
- ✅ Retrieval tests passed (real data retrieved, not placeholders)
- ✅ Answer quality improved (more confident, fewer disclaimers)

### Risks and Mitigations

**Risk 1: Real data delayed**
- **Impact:** Placeholders remain longer than expected
- **Mitigation:** Phased replacement (replace as data arrives, not all at once)
- **Rollback:** Continue with placeholders until real data available

**Risk 2: Real data quality issues**
- **Impact:** Incorrect product/provider information
- **Mitigation:** Data validation before ingestion, compliance review
- **Rollback:** Revert to placeholder, fix real data, re-ingest

**Risk 3: Mapping update errors**
- **Impact:** FAQ/Rules no longer link to correct plans
- **Mitigation:** Automated mapping update script, validation
- **Rollback:** Restore old mappings, fix errors, re-update

### Validation Gate
**Go/No-Go Criteria for Phase E:**
- ✅ At least 50% real Plan data ingested (5 of 10 plans)
- ✅ At least 50% real Network data ingested (5 of 10 providers)
- ✅ Replacement validation passed for all new chunks
- ✅ Answer quality metrics improved
- ✅ NO critical bugs

**If NO-GO:** Fix issues, complete more replacements, re-validate

### Timeline
**Estimated Duration:** 3-6 months (depends on data availability)  
**Plans:** 6 months expected  
**Network:** 3 months expected  
**Dependencies:** Phase C completed, real data available  
**Team:** Data engineers, product team, provider contracts team, QA engineers  

---

## 6. Phase E: Production Hardening and Optimization

### Goal
Optimize system for production performance, reliability, and continuous improvement

### Scope
**IN SCOPE:**
- Performance optimization (retrieval latency, throughput)
- Monitoring and alerting (placeholder leaks, answer quality, retrieval distribution)
- Continuous content improvement (add new FAQ, update Rules, improve Mapping)
- User feedback loop (collect feedback, identify gaps, prioritize updates)
- Compliance and governance (quarterly audits, annual review)

**OUT OF SCOPE:**
- Major architectural changes (foundation established)

### Prerequisites
- ✅ Phase D completed (majority of real data ingested)
- ✅ Production environment deployed
- ✅ Monitoring infrastructure ready

### Process Steps

**Step 1: Performance optimization**
- Optimize embedding model inference
- Optimize vector database query performance
- Cache frequent queries
- Load balancing

**Step 2: Implement monitoring**
- Placeholder leak detection (real-time)
- Retrieval weight distribution (daily)
- Answer quality by source (weekly)
- FAQ coverage rate (weekly)
- User satisfaction scores (weekly)

**Step 3: Implement alerting**
- CRITICAL: Placeholder leak detected
- HIGH: Retrieval performance degraded
- MEDIUM: Answer quality below threshold
- LOW: FAQ coverage gap detected

**Step 4: Content improvement loop**
```
User feedback → Gap identification → Content creation → Ingestion → Validation → Deployment
```

**Step 5: Compliance and governance**
- Quarterly audit (100 sample interactions, 0% placeholder leak)
- Annual comprehensive review (all 87+ chunks, metadata accuracy, policy compliance)
- Compliance certification

### Outputs
- Performance benchmarks (latency, throughput)
- Monitoring dashboards (real-time metrics)
- Alert rules (automated incident detection)
- Content improvement roadmap (quarterly)
- Compliance audit reports (quarterly, annually)

### Success Criteria
- ✅ Retrieval latency <500ms (p95)
- ✅ Placeholder leak rate 0% (continuous)
- ✅ FAQ coverage rate >80%
- ✅ Answer quality HIGH >70%
- ✅ User satisfaction >4.0/5.0
- ✅ Quarterly audits passed (0% placeholder leaks)

### Risks and Mitigations

**Risk 1: Performance degradation over time**
- **Impact:** Poor user experience
- **Mitigation:** Continuous monitoring, performance testing, optimization
- **Rollback:** Scale infrastructure, optimize queries

**Risk 2: Content stale**
- **Impact:** Answers outdated, user dissatisfaction
- **Mitigation:** Content improvement loop, regular reviews
- **Rollback:** Accelerate content updates

**Risk 3: Compliance issues**
- **Impact:** Regulatory penalties, legal liability
- **Mitigation:** Quarterly audits, placeholder leak monitoring, compliance team involvement
- **Rollback:** Fix issues immediately, incident reporting

### Validation Gate
**Production Readiness Criteria:**
- ✅ All previous phases completed
- ✅ Performance benchmarks met
- ✅ Monitoring and alerting functional
- ✅ Content improvement loop established
- ✅ Compliance audit passed

**Ongoing Production Criteria:**
- ✅ Placeholder leak rate 0% (continuous)
- ✅ Performance within SLA
- ✅ Quarterly audits passed

### Timeline
**Estimated Duration:** Ongoing (continuous improvement)  
**Dependencies:** Phase D completed  
**Team:** Data engineers, ML engineers, QA engineers, product team, compliance team  

---

## 7. Phase Summary Table

| Phase | Goal | Duration | Key Outputs | Success Metric |
|-------|------|----------|-------------|----------------|
| **A** | Metadata-Ready Intake | 2-3 days | Validated chunks with metadata | 0 metadata errors |
| **B** | FAQ+Rules+Mapping Only | 1-2 weeks | 67 chunks indexed, retrieval tested | FAQ relevance >85% |
| **C** | Placeholder-Aware | 2-3 weeks | 87 chunks, filtering/safety tested | Placeholder leak 0% |
| **D** | Real Data Replacement | 3-6 months | Real plan/network data ingested | 50%+ real data |
| **E** | Production Hardening | Ongoing | Monitoring, optimization, compliance | Leak 0%, Quality HIGH |

---

## 8. Rollback Strategy

### Rollback from Phase C to Phase B
**Trigger:** Placeholder leaks detected, filtering failures  
**Actions:**
1. Remove Phase 2 chunks (Plans/Network placeholders) from vector DB
2. Revert to 67-chunk configuration
3. Fix filtering/safety logic
4. Re-run Phase C validation
5. Re-deploy with fixed logic

### Rollback from Phase D to Phase C
**Trigger:** Real data quality issues, replacement errors  
**Actions:**
1. Deprecate new real data chunks
2. Un-deprecate old placeholders (temporary)
3. Fix real data quality issues
4. Re-run Phase D replacement process
5. Validate and re-deploy

### Full Rollback
**Trigger:** Critical system failure, major bugs  
**Actions:**
1. Restore vector DB backup (from last stable phase)
2. Restore application code (from last stable version)
3. Investigate root cause
4. Fix issues
5. Re-test thoroughly
6. Re-deploy from stable phase

---

## 9. Document Control

**Filename:** IMPLEMENTATION_PHASES.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- INGESTION_SEQUENCE.md - Exact ingestion order
- METADATA_APPLICATION_SPEC.md - Metadata derivation
- CHUNK_FILTERING_RULES.md - Filtering logic
- PLACEHOLDER_ENFORCEMENT_SPEC.md - Placeholder rules
- ANSWER_SAFETY_BEHAVIOR.md - Answer generation
- VALIDATION_AND_QA_SPEC.md - Testing and QA
- DEPLOYMENT_READINESS_GATES.md - Go/No-Go criteria

---

**END OF IMPLEMENTATION PHASES SPECIFICATION**

**CRITICAL REMINDER:** Deploy incrementally, validate thoroughly at each phase, enable rollback capability.
