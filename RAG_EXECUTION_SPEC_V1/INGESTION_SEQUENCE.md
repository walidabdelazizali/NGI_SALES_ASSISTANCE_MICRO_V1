# RAG Ingestion Sequence Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define exact ingestion order and sequencing for KB_PACK_V1

---

## 1. Overview

This document specifies the **exact order** in which KB_PACK_V1 JSONL files should be ingested into a future RAG system.

### Why Sequencing Matters

1. **Trust Hierarchy** - FAQ and Rules are foundational; Mapping and Placeholders are supplementary
2. **Dependency Order** - Mapping references FAQ and Rules; placeholders should not override strong knowledge
3. **Risk Mitigation** - Ingest high-confidence content first, low-confidence content last with extra guardrails
4. **Testing Progression** - Validate strong knowledge before adding weaker or placeholder content
5. **Rollback Simplicity** - If issues arise, can roll back to last known good state (e.g., "Phase 1 only")

---

## 2. Two-Phase Ingestion Strategy

### Phase 1: Strong Knowledge Foundation (HIGH PRIORITY)
**Goal:** Establish reliable, customer-facing knowledge base  
**Content:** FAQ + Rules + Mapping (67 chunks)  
**Confidence:** High to Medium  
**Risk:** Low  

### Phase 2: Placeholder-Aware Context Layer (LOW PRIORITY, HIGH CAUTION)
**Goal:** Add routing awareness and prepare for future real data  
**Content:** Plans + Network (20 placeholder chunks)  
**Confidence:** Very Low (structural only)  
**Risk:** High (easily misinterpreted)  

**CRITICAL:** Phase 2 should NOT be deployed to customer-facing systems unless strict placeholder filtering or heavy disclaimers are enforced.

---

## 3. Phase 1 Ingestion Sequence

### Step 1.1: Ingest FAQ Chunks
**File:** `KB_PACK_V1/faq_chunks.jsonl`  
**Count:** 20 FAQ chunks  
**Status Breakdown:**
- 9 Approved
- 7 Needs Review
- 4 Pending Detail

**Priority:** CRITICAL - FAQ chunks are the primary customer-facing knowledge

**Ingestion Order:**
1. **FAQ Approved** (9 chunks) - Highest priority, direct customer use
2. **FAQ Needs Review** (7 chunks) - High priority, may require light disclaimers
3. **FAQ Pending Detail** (4 chunks) - Medium priority, require operational detail disclaimers

**Metadata Requirements:**
- `chunk_type: "FAQ"`
- `is_placeholder: false` (all FAQ chunks are real content)
- `safe_for_client_direct_use: true` (for Approved), `true` (for Needs Review with disclaimers), `true` (for Pending Detail with operational disclaimers)
- `retrieval_weight_hint: 1.0` (Approved), `0.95` (Needs Review), `0.9` (Pending Detail)
- `requires_plan_confirmation: true` (if FAQ is plan-specific, e.g., FAQ-005 "Does my plan cover dental?")

**Expected Outcome:** FAQ retrieval returns relevant questions with high confidence

**Validation Check:** 20 FAQ chunks indexed successfully, FAQ Approved chunks retrievable with weight ≥1.0

---

### Step 1.2: Ingest Rules Chunks
**File:** `KB_PACK_V1/rules_chunks.jsonl`  
**Count:** 27 Rules chunks  
**Status Breakdown:**
- 26 Active
- 1 Needs Review (RULE-008)

**Priority:** CRITICAL - Rules provide reasoning and policy explanation to support FAQ answers

**Ingestion Order:**
1. **Rules Active** (26 chunks) - Highest priority, safe for reasoning
2. **Rules Needs Review** (1 chunk: RULE-008) - Requires compliance review before direct customer use

**Metadata Requirements:**
- `chunk_type: "Rules"`
- `is_placeholder: false` (all Rules are real policy content)
- `safe_for_client_direct_use: true` (for Active), `false` (for RULE-008 Needs Review pending compliance check)
- `retrieval_weight_hint: 0.9` (Active), `0.85` (Needs Review)
- `requires_policy_caution: true` (for RULE-008 and any rules with sensitive policy language)

**Expected Outcome:** Rules retrieval provides detailed reasoning and policy explanations to enrich FAQ answers

**Validation Check:** 27 Rules chunks indexed successfully, Active Rules retrievable with weight ≥0.9

---

### Step 1.3: Ingest Mapping Chunks
**File:** `KB_PACK_V1/mapping_reference.jsonl`  
**Count:** 20 Mapping chunks  
**Confidence Breakdown:**
- 16 High/Medium Confidence
- 3 Low Confidence (MAP-012, MAP-013, MAP-017)
- 1 mapping links to placeholder plan (MAP-005)

**Priority:** MEDIUM - Mapping provides cross-reference enrichment, NOT primary content

**Ingestion Order:**
1. **Mapping High Confidence** - Safe for cross-reference
2. **Mapping Medium Confidence** - Safe for cross-reference with awareness
3. **Mapping Low Confidence** - Use with caution, add disclaimers if primary evidence

**Metadata Requirements:**
- `chunk_type: "Mapping"`
- `is_placeholder: false` (mappings are real relationships, even if pointing to placeholders)
- `safe_for_client_direct_use: false` (mappings are reference layer, not customer-facing content)
- `retrieval_weight_hint: 0.6` (High confidence), `0.5` (Medium confidence), `0.4` (Low confidence)
- `needs_plan_link: true` (if mapping references a plan)
- `needs_rule_link: true` (if mapping references a rule)

**Expected Outcome:** Mapping enables cross-reference enrichment (e.g., FAQ-005 → RULE-003 → PLAN-003 placeholder, with appropriate handling)

**Validation Check:** 20 Mapping chunks indexed successfully, cross-reference links functional

---

### Phase 1 Summary

**Total Chunks:** 67  
**Total Files:** 3 (faq_chunks.jsonl, rules_chunks.jsonl, mapping_reference.jsonl)  
**Ingestion Time:** All 3 files can be ingested in parallel or sequentially (FAQ → Rules → Mapping recommended for testing)  
**Confidence Level:** High to Medium  
**Customer-Facing Readiness:** READY (with appropriate disclaimers for Needs Review, Pending Detail, and plan/network-specific questions)  

**Phase 1 Success Criteria:**
- ✅ 67 chunks indexed successfully
- ✅ FAQ Approved chunks retrieve with high relevance (>85% for sample queries)
- ✅ Rules Active chunks provide reasoning support
- ✅ Mapping cross-references functional
- ✅ No placeholder content indexed yet (Phase 2 not started)

---

## 4. Phase 2 Ingestion Sequence

**⚠️ CRITICAL WARNING:** Phase 2 ingestion adds placeholder content that is NOT confirmed product/provider data. Strict guardrails MUST be enforced before any customer-facing deployment.

---

### Step 2.1: Ingest Plans Placeholder Chunks
**File:** `KB_PACK_V1/plans_chunks.jsonl`  
**Count:** 10 Plan placeholder chunks  
**Status:** ALL "Pending Detail"  
**is_placeholder:** ALL true

**Priority:** LOW - Placeholder content for routing awareness only

**Ingestion Order:**
- All 10 plan placeholders can be ingested together (order doesn't matter within this file)

**Metadata Requirements (MANDATORY):**
- `chunk_type: "Plans"`
- `is_placeholder: true` ← **CRITICAL SAFETY FLAG**
- `safe_for_client_direct_use: false` ← **MUST BE FALSE**
- `retrieval_weight_hint: 0.2` ← **VERY LOW WEIGHT**
- `requires_plan_confirmation: true`
- `requires_policy_caution: true`

**Expected Outcome:** Plan placeholders enable:
- ✅ Question routing ("This is a Basic Family Plan question")
- ✅ Context awareness ("User is asking about plan benefits")
- ✅ Gap identification ("We don't have real plan data yet")

**Expected Outcome (FORBIDDEN):**
- ❌ Confirming plan benefits ("Basic Family Plan covers dental")
- ❌ Comparing plans ("Basic Plan is cheaper than Premium Plan")
- ❌ Calculating costs ("Your deductible is AED 500")

**Validation Check:** 
- 10 Plan chunks indexed successfully
- ALL have `is_placeholder: true`
- ALL have `safe_for_client_direct_use: false`
- ALL have `retrieval_weight_hint ≤ 0.3`
- Placeholder filter test: Customer-facing query does NOT return placeholder plans as confirmed benefits

---

### Step 2.2: Ingest Network Placeholder Chunks
**File:** `KB_PACK_V1/network_chunks.jsonl`  
**Count:** 10 Network placeholder chunks  
**Status:** ALL "Pending Detail"  
**is_placeholder:** ALL true

**Priority:** LOW - Placeholder content for routing awareness only

**Ingestion Order:**
- All 10 network placeholders can be ingested together (order doesn't matter within this file)

**Metadata Requirements (MANDATORY):**
- `chunk_type: "Network"`
- `is_placeholder: true` ← **CRITICAL SAFETY FLAG**
- `safe_for_client_direct_use: false` ← **MUST BE FALSE**
- `retrieval_weight_hint: 0.2` ← **VERY LOW WEIGHT**
- `requires_network_verification: true`

**Expected Outcome:** Network placeholders enable:
- ✅ Question routing ("This is a provider network question")
- ✅ Context awareness ("User is asking about Dubai Medical Center")
- ✅ Gap identification ("We don't have verified provider data yet")

**Expected Outcome (FORBIDDEN):**
- ❌ Confirming provider network status ("Dubai Medical Center is in-network")
- ❌ Recommending providers ("Visit Dubai Medical Center for treatment")
- ❌ Guiding appointments ("Dubai Medical Center accepts your plan")

**Validation Check:** 
- 10 Network chunks indexed successfully
- ALL have `is_placeholder: true`
- ALL have `safe_for_client_direct_use: false`
- ALL have `retrieval_weight_hint ≤ 0.3`
- Placeholder filter test: Customer-facing query does NOT return placeholder network as confirmed provider directory

---

### Phase 2 Summary

**Total Chunks:** 20 (10 Plans + 10 Network)  
**Total Files:** 2 (plans_chunks.jsonl, network_chunks.jsonl)  
**Ingestion Time:** Both files can be ingested in parallel  
**Confidence Level:** Very Low (structural placeholders only)  
**Customer-Facing Readiness:** NOT READY without strict filtering or heavy disclaimers  

**Phase 2 Success Criteria:**
- ✅ 20 placeholder chunks indexed successfully
- ✅ ALL placeholders tagged with `is_placeholder: true`
- ✅ ALL placeholders have `safe_for_client_direct_use: false`
- ✅ ALL placeholders have very low retrieval weight (0.2)
- ✅ Placeholder filter test passes (no placeholders leak to customer answers as confirmed facts)
- ✅ Disclaimer test passes (if placeholders used, heavy disclaimers added)

---

## 5. Complete Ingestion Order (Both Phases)

### Recommended Sequential Order

```
Phase 1 (Strong Knowledge - DEPLOY FIRST)
│
├─ Step 1.1: FAQ Chunks (20 chunks)
│   └─ Priority order: Approved → Needs Review → Pending Detail
│
├─ Step 1.2: Rules Chunks (27 chunks)
│   └─ Priority order: Active → Needs Review
│
├─ Step 1.3: Mapping Chunks (20 chunks)
│   └─ Priority order: High Confidence → Medium → Low Confidence
│
└─ Phase 1 Validation Gate ✅

Phase 2 (Placeholder Awareness - DEPLOY WITH CAUTION)
│
├─ Step 2.1: Plans Placeholder Chunks (10 chunks)
│   └─ ALL placeholders, ALL low priority
│
├─ Step 2.2: Network Placeholder Chunks (10 chunks)
│   └─ ALL placeholders, ALL low priority
│
└─ Phase 2 Validation Gate ✅ (includes placeholder leak detection)
```

### Alternative: Parallel Ingestion (Fast, Requires Strong Metadata Enforcement)

If implementation supports parallel ingestion:
- Files can be ingested simultaneously
- Metadata MUST be applied correctly during ingestion (not post-hoc)
- Retrieval weights must be enforced from first query
- Validation must check all 87 chunks before any customer-facing deployment

**Parallel Ingestion Risk:** Harder to test incrementally, harder to rollback granularly.

**Recommendation:** Sequential ingestion (FAQ → Rules → Mapping → Plans → Network) for first deployment, parallel for subsequent updates.

---

## 6. Re-Ingestion Scenarios

### Scenario A: Content Update (FAQ or Rules)
**Trigger:** FAQ or Rule content revised, status changed (e.g., "Needs Review" → "Approved")

**Process:**
1. Update source content in KB_PACK_V1 (create new version, e.g., KB_PACK_V1.1)
2. Re-ingest updated FAQ or Rules file
3. Metadata should reflect new status and potentially updated retrieval weight
4. Re-generate embeddings for updated chunks only (incremental update)
5. Validate updated chunks retrieve correctly
6. Monitor for impact on answer quality

**No need to re-ingest other files** unless dependencies changed.

---

### Scenario B: Placeholder Replacement with Real Data (HIGH PRIORITY)
**Trigger:** Real plan data or provider network data becomes available

**Example:** PLAN-003 "Basic Family Plan" placeholder is replaced with real approved product documentation

**Process:**
1. Create new chunk with real plan data in KB_PACK_V2 (e.g., `PLAN-CHUNK-103` with `plan_id: "PLAN-103"`)
2. Set metadata:
   - `is_placeholder: false` ← **CRITICAL CHANGE**
   - `safe_for_client_direct_use: true`
   - `retrieval_weight_hint: 0.9` (significantly higher than 0.2)
   - `supersedes: "PLAN-003"` (link to old placeholder)
3. Mark old placeholder PLAN-003 as deprecated:
   - `status: "Deprecated"`
   - `deprecated_date: "2026-06-01"`
   - `superseded_by: "PLAN-103"`
4. Remove old placeholder from active retrieval (within 30 days)
5. Update any mappings that referenced PLAN-003 to reference PLAN-103
6. Re-ingest:
   - New real plan chunk (PLAN-103)
   - Updated mapping chunks (if applicable)
7. Validate:
   - Old placeholder no longer retrieved
   - New real plan retrieved with high weight
   - Mappings correctly reference new plan
   - Answer no longer requires disclaimer for this plan

**Timeline:** Plans (6 months), Network (3 months) - see RAG_POLICY_V1/PLACEHOLDER_HANDLING_POLICY.md

---

### Scenario C: Mapping Update (Low/Medium Confidence → High Confidence)
**Trigger:** Provisional mapping refined, confidence increased

**Example:** MAP-012 (login issues) currently maps to RULE-016 (Terms of Service) with Low Confidence. New operational rule created (RULE-028: Technical Support), mapping updated to reference new rule with High Confidence.

**Process:**
1. Create new rule RULE-028 in KB_PACK_V2
2. Update MAP-012:
   - `primary_rule_id: "RULE-028"` (was "RULE-016")
   - `confidence: "High"` (was "Low")
   - `retrieval_weight_hint: 0.6` (was 0.4)
3. Re-ingest:
   - New rule chunk (RULE-028)
   - Updated mapping chunk (MAP-012)
4. Validate:
   - MAP-012 now retrieves with higher confidence
   - Cross-reference to RULE-028 functional

---

### Scenario D: Bulk Re-Ingestion (Major KB Update)
**Trigger:** 20%+ of KB content changed, or new KB version released (KB_PACK_V2)

**Process:**
1. Follow same ingestion sequence (Phase 1 → Phase 2)
2. May require full re-embedding if embedding model changed
3. Validate entire KB after re-ingestion
4. Compare retrieval quality before/after (regression testing)
5. Consider gradual rollout (A/B test old vs new KB)

**Timeline:** Quarterly or as major content updates occur

---

## 7. Ingestion Process Checklist

### Pre-Ingestion
- [ ] KB_PACK_V1 files available and validated (JSON format correct)
- [ ] Metadata schema defined and implemented
- [ ] Embedding model chosen and tested
- [ ] Vector database configured
- [ ] Ingestion pipeline built and tested on sample data

### During Ingestion
- [ ] Phase 1 files ingested in order (FAQ → Rules → Mapping)
- [ ] Metadata applied correctly to each chunk
- [ ] Embeddings generated successfully
- [ ] Chunks stored in vector DB with metadata
- [ ] Phase 1 validation passed before Phase 2

### Post-Ingestion Phase 1
- [ ] 67 chunks indexed (20 FAQ + 27 Rules + 20 Mapping)
- [ ] Required metadata fields present on all chunks
- [ ] Retrieval weights set correctly
- [ ] Sample queries return relevant FAQ/Rules
- [ ] Cross-references functional (Mapping → FAQ/Rules)
- [ ] No errors or missing chunks

### During Phase 2 (If Proceeding)
- [ ] Placeholder files ingested (Plans → Network)
- [ ] ALL placeholders tagged with `is_placeholder: true`
- [ ] ALL placeholders marked `safe_for_client_direct_use: false`
- [ ] Low retrieval weights applied (0.2)

### Post-Ingestion Phase 2
- [ ] 87 chunks indexed (67 Phase 1 + 20 Phase 2)
- [ ] Placeholder filter test passed (no leaks)
- [ ] Disclaimer test passed (plan/network queries include warnings)
- [ ] Phase 1 chunks still retrieve properly (not degraded by Phase 2)

### Validation (Both Phases)
- [ ] Run validation scenarios (see VALIDATION_AND_QA_SPEC.md)
- [ ] Check deployment readiness gates (see DEPLOYMENT_READINESS_GATES.md)
- [ ] Document ingestion results (chunk counts, metadata completeness, test results)

---

## 8. Rollback and Recovery

### Rollback to Phase 1 Only
**Trigger:** Phase 2 placeholder content causing issues (leaks, quality degradation)

**Process:**
1. Remove Phase 2 chunks from vector DB (10 Plans + 10 Network)
2. Revert to 67-chunk configuration (Phase 1 only)
3. Validate retrieval quality restored
4. Investigate Phase 2 issues offline
5. Re-deploy Phase 2 only after fixes validated

**Advantage of Sequential Ingestion:** Easy to rollback to last known good phase.

---

### Full Rollback
**Trigger:** Major issues with entire KB ingestion

**Process:**
1. Restore previous vector DB backup (if available)
2. Or re-ingest from previous KB_PACK version
3. Validate retrieval quality
4. Investigate issues with new version offline
5. Fix and re-ingest incrementally

**Prevention:** Always backup vector DB before major ingestion updates.

---

## 9. Maintenance Schedule

### Weekly
- Monitor retrieval quality metrics
- Check for errors or missing chunks
- Track placeholder leak incidents (if Phase 2 deployed)

### Monthly
- Content accuracy audit (sample 10-20 chunks, verify against sources)
- Metadata accuracy check (spot-check required fields)
- Broken link check (Mapping cross-references)

### Quarterly
- Comprehensive KB review (all 87 chunks)
- Placeholder replacement progress assessment
- Policy compliance review (guardrails enforced correctly)
- Performance review (retrieval latency, relevance scores)

### Annually
- Full KB certification (legal/compliance review)
- Technology refresh (embedding model, vector DB upgrades)
- Strategic planning (new content, new use cases)

---

## 10. Key Decisions and Rationale

### Why FAQ First?
FAQ chunks are customer-facing and represent most common questions. If FAQ retrieval works well, system delivers immediate value.

### Why Rules Second?
Rules provide reasoning to enrich FAQ answers. FAQ + Rules together enable comprehensive answers with explanation.

### Why Mapping Third?
Mapping references FAQ and Rules. Ingesting mapping before its dependencies would create broken references.

### Why Placeholders Last?
Placeholders have very low confidence and high risk. Should only be added after strong knowledge foundation validated.

### Why Not Ingest Placeholders at All?
Valid choice for initial deployment. If organization wants to minimize risk, deploy Phase 1 only until real plan/network data available.

---

## 11. Document Control

**Filename:** INGESTION_SEQUENCE.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- EXECUTION_OVERVIEW.md - Master reference
- METADATA_APPLICATION_SPEC.md - How to apply metadata during ingestion
- VALIDATION_AND_QA_SPEC.md - Post-ingestion validation checks

---

**END OF INGESTION SEQUENCE SPECIFICATION**

Follow this sequence to ensure safe, validated, incremental ingestion of KB_PACK_V1.
