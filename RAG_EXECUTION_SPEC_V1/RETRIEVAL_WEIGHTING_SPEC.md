# Retrieval Weighting Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define practical retrieval weighting strategy by chunk type

---

## 1. Overview

This specification defines **how retrieval weights should be calculated and applied** to ensure FAQ and Rules dominate retrieval while placeholders are appropriately downranked.

### Why Weights Matter

Without proper weighting:
- ❌ Placeholder content with good semantic match could outrank FAQ/Rules
- ❌ Low-confidence Mapping could appear as primary evidence
- ❌ Trust hierarchy (FAQ/Rules > Mapping > Placeholders) not enforced

With proper weighting:
- ✅ FAQ and Rules dominate top results
- ✅ Placeholders appear only rarely and with very low scores
- ✅ Trust hierarchy maintained algorithmically

---

## 2. Weight Calculation Formula

### Base Formula

```
final_retrieval_score = semantic_similarity_score × retrieval_weight_hint × status_multiplier × use_case_multiplier
```

**Components:**
1. **semantic_similarity_score** (0.0-1.0) - From vector similarity (cosine, dot product, etc.)
2. **retrieval_weight_hint** (0.0-1.0) - From metadata (see METADATA_APPLICATION_SPEC.md)
3. **status_multiplier** (0.0-1.0) - Based on chunk status (Approved/Active = 1.0, Needs Review = 0.9, etc.)
4. **use_case_multiplier** (0.0-1.0) - Based on use case (customer-facing more strict)

---

### Example Calculations

**Example 1: FAQ Approved (Strong)**
```
semantic_similarity_score = 0.85
retrieval_weight_hint = 1.0
status_multiplier = 1.0 (Approved)
use_case_multiplier = 1.0 (customer-facing)

final_score = 0.85 × 1.0 × 1.0 × 1.0 = 0.85
```

**Example 2: Plan Placeholder (Weak)**
```
semantic_similarity_score = 0.85 (same semantic match!)
retrieval_weight_hint = 0.2 (placeholder)
status_multiplier = 0.8 (Pending Detail)
use_case_multiplier = 0.5 (customer-facing downrank)

final_score = 0.85 × 0.2 × 0.8 × 0.5 = 0.068
```

**Result:** FAQ scores **12.5x higher** than placeholder despite identical semantic match.

---

## 3. Retrieval Weight Matrix

### Master Weight Matrix

| Chunk Type | Status | is_placeholder | Base Weight | Status Multiplier | Effective Range |
|------------|--------|----------------|-------------|-------------------|-----------------|
| **FAQ** | Approved | false | 1.0 | 1.0 | 1.0 |
| FAQ | Needs Review | false | 0.95 | 0.95 | 0.90-0.95 |
| FAQ | Pending Detail | false | 0.9 | 0.90 | 0.81-0.90 |
| **Rules** | Active | false | 0.9 | 1.0 | 0.9 |
| Rules | Needs Review | false | 0.85 | 0.90 | 0.77-0.85 |
| **Mapping** | High Confidence | false | 0.6 | 1.0 | 0.6 |
| Mapping | Medium Confidence | false | 0.5 | 1.0 | 0.5 |
| Mapping | Low Confidence | false | 0.4 | 0.90 | 0.36-0.40 |
| **Plans** | Pending Detail | true | 0.2 | 0.80 | 0.16 |
| **Network** | Pending Detail | true | 0.2 | 0.80 | 0.16 |

**Notes:**
- **Effective Range:** Final weight after applying status multiplier
- **Customer-facing:** May apply additional use_case_multiplier (e.g., 0.5 for placeholders = 0.08 effective weight)
- **Base Weight:** Stored in metadata as `retrieval_weight_hint`

---

### Weight Tiers (Simplified)

**Tier 1: Primary Knowledge (0.85-1.0)**
- FAQ Approved (1.0)
- FAQ Needs Review (0.95)
- FAQ Pending Detail (0.9)
- Rules Active (0.9)

**Use:** Direct customer answers, high confidence

---

**Tier 2: Supporting Knowledge (0.4-0.85)**
- Rules Needs Review (0.85)
- Mapping High Confidence (0.6)
- Mapping Medium Confidence (0.5)
- Mapping Low Confidence (0.4)

**Use:** Context enrichment, reasoning support, cross-reference

---

**Tier 3: Placeholder Knowledge (0.16-0.2)**
- Plans Placeholder (0.2 → 0.16 effective)
- Network Placeholder (0.2 → 0.16 effective)

**Use:** Question routing, context awareness only. NEVER direct customer answers.

---

## 4. Status Multipliers

### Status-Based Adjustments

| Status | Multiplier | Rationale |
|--------|-----------|-----------|
| Approved | 1.0 | No penalty - fully approved content |
| Active | 1.0 | No penalty - active policy rules |
| Needs Review | 0.90-0.95 | Small penalty - requires review before full confidence |
| Pending Detail | 0.80-0.90 | Moderate penalty - incomplete or awaiting finalization |
| Deprecated | 0.0 | Complete exclusion - outdated content |

**Implementation:**
```python
status_multiplier = {
    "Approved": 1.0,
    "Active": 1.0,
    "Needs Review": 0.95,
    "Pending Detail": 0.90,
    "Deprecated": 0.0,  # Filter out completely
}[chunk.status]
```

---

## 5. Use Case Multipliers

### Customer-Facing (Strict)

| Chunk Characteristic | Multiplier | Rationale |
|---------------------|-----------|-----------|
| is_placeholder = true | 0.5 or 0.0 | Heavy downrank or exclude completely |
| safe_for_client_direct_use = false | 0.8 | Downrank, prefer safer alternatives |
| confidence = "Low" or "Very Low" | 0.7 | Downrank low-confidence content |
| chunk_type = "Mapping" | 0.8 | Downrank (reference support, not primary) |

**Recommended:** Apply placeholder multiplier of 0.0 (complete exclusion) for customer-facing retrieval.

---

### Internal Assistant (Moderate)

| Chunk Characteristic | Multiplier | Rationale |
|---------------------|-----------|-----------|
| is_placeholder = true | 0.8 | Show with warnings, but downrank |
| safe_for_client_direct_use = false | 1.0 | Internal users can handle |
| confidence = "Low" or "Very Low" | 0.9 | Less strict than customer-facing |
| chunk_type = "Mapping" | 1.0 | Useful for understanding relationships |

---

### Self-Service FAQ (Very Strict)

| Chunk Characteristic | Multiplier | Rationale |
|---------------------|-----------|-----------|
| chunk_type != "FAQ" | 0.0 | Exclude non-FAQ (too complex) |
| status != "Approved" | 0.0 | Exclude non-approved (not ready) |
| confidence != "High" | 0.0 | Exclude medium/low confidence |

---

## 6. Chunk Type-Specific Weighting

### FAQ Weights (20 chunks)

**FAQ-001 through FAQ-009: Approved (9 chunks)**
- Base Weight: **1.0**
- Status Multiplier: 1.0
- Effective Weight: **1.0**
- **Use:** Primary customer-facing answers
- **Confidence:** High (90-100%)

**FAQ with Needs Review (7 chunks)**
- Base Weight: **0.95**
- Status Multiplier: 0.95
- Effective Weight: **0.90-0.95**
- **Use:** Customer-facing with light disclaimers
- **Confidence:** Medium-High (70-90%)

**FAQ-011, FAQ-013, FAQ-017, FAQ-020: Pending Detail (4 chunks)**
- Base Weight: **0.9**
- Status Multiplier: 0.90
- Effective Weight: **0.81**
- **Use:** Customer-facing with operational disclaimers ("Contact customer service for specific instructions")
- **Confidence:** Medium (50-70%)
- **Characteristics:** General guidance available, specific operational details pending

---

### Rules Weights (27 chunks)

**RULE-001 through RULE-027 (excluding RULE-008): Active (26 chunks)**
- Base Weight: **0.9**
- Status Multiplier: 1.0
- Effective Weight: **0.9**
- **Use:** Policy reasoning, FAQ enrichment
- **Confidence:** High (90-100%)

**RULE-008: Needs Review (1 chunk)**
- Base Weight: **0.85**
- Status Multiplier: 0.90
- Effective Weight: **0.77**
- **Use:** Internal reference only until compliance review
- **Confidence:** Medium (60-80%)
- **Note:** Requires legal/compliance approval before customer-facing use

---

### Mapping Weights (20 chunks)

**High Confidence Mappings (e.g., MAP-001 through MAP-011) (~16 chunks)**
- Base Weight: **0.6**
- Status Multiplier: 1.0
- Effective Weight: **0.6**
- **Use:** Cross-reference enrichment, relationship awareness
- **Confidence:** Medium (60-80%)

**Medium Confidence Mappings (~1 chunk)**
- Base Weight: **0.5**
- Status Multiplier: 1.0
- Effective Weight: **0.5**
- **Use:** Cross-reference with awareness of medium confidence

**MAP-012, MAP-013, MAP-017: Low Confidence (3 chunks)**
- Base Weight: **0.4**
- Status Multiplier: 0.90
- Effective Weight: **0.36**
- **Use:** Provisional cross-reference, add disclaimers if primary evidence
- **Confidence:** Low-Medium (30-50%)
- **Characteristics:** Tangential relationships, awaiting dedicated operational rules

**Important:** Mapping chunks should NEVER be displayed directly to customers. Use for finding related FAQ/Rules only.

---

### Plans Weights (10 chunks - ALL PLACEHOLDERS)

**PLAN-001 through PLAN-010: Pending Detail, Placeholder (10 chunks)**
- Base Weight: **0.2**
- Status Multiplier: 0.80
- Use Case Multiplier: 0.5 (customer-facing) or 0.8 (internal)
- Effective Weight: **0.08 (customer)** or **0.128 (internal)**
- **Use:** Question routing, context awareness ONLY
- **Confidence:** Very Low (0-20%) - Structural placeholders, NOT confirmed product data
- **CRITICAL:** is_placeholder = true, safe_for_client_direct_use = false

**Why So Low:**
- Prevents placeholders from EVER outranking FAQ/Rules
- Even with perfect semantic match (1.0), placeholder scores max 0.2 vs FAQ 1.0
- Ensures trust hierarchy maintained algorithmically

---

### Network Weights (10 chunks - ALL PLACEHOLDERS)

**PROV-001 through PROV-010: Pending Detail, Placeholder (10 chunks)**
- Base Weight: **0.2**
- Status Multiplier: 0.80
- Use Case Multiplier: 0.5 (customer-facing) or 0.8 (internal)
- Effective Weight: **0.08 (customer)** or **0.128 (internal)**
- **Use:** Question routing, provider type awareness ONLY
- **Confidence:** Very Low (0-20%) - Structural placeholders, NOT verified provider directory
- **CRITICAL:** is_placeholder = true, safe_for_client_direct_use = false

**Why So Low:**
- Same rationale as Plans placeholders
- Prevents unverified provider data from appearing as confirmed network status
- Customer must verify with authoritative provider directory or customer service

---

## 7. Weight Application Scenarios

### Scenario 1: General Insurance Question

**Query:** "What is a deductible?"

**Retrieval:**
1. FAQ-001 "What is a deductible?" (Approved)
   - Semantic: 0.95, Weight: 1.0 → **Final: 0.95**
2. RULE-001 "Deductible Application" (Active)
   - Semantic: 0.80, Weight: 0.9 → **Final: 0.72**
3. MAP-001 (FAQ-001 → RULE-001)
   - Semantic: 0.70, Weight: 0.6 → **Final: 0.42**

**Result:** FAQ dominates (0.95), Rule provides enrichment (0.72), Mapping provides cross-reference context (0.42). Trust hierarchy maintained.

---

### Scenario 2: Plan-Specific Question (Placeholder Risk)

**Query:** "Does Basic Family Plan cover dental?"

**Retrieval:**
1. FAQ-005 "Does my plan cover dental?" (Approved)
   - Semantic: 0.90, Weight: 1.0 → **Final: 0.90**
2. RULE-003 "Benefit Categories" (Active)
   - Semantic: 0.75, Weight: 0.9 → **Final: 0.675**
3. MAP-005 (FAQ-005 → RULE-003 → PLAN-003)
   - Semantic: 0.80, Weight: 0.6 → **Final: 0.48**
4. PLAN-003 "Basic Family Plan" (Placeholder)
   - Semantic: 0.95, Weight: 0.2 × 0.8 × 0.5 = 0.08 → **Final: 0.076**

**Result:** FAQ dominates (0.90), Rule enriches (0.675), Mapping cross-references (0.48), Placeholder heavily downranked (0.076). Answer defers to policy documents for plan-specific details.

**Answer Strategy:**
- Use FAQ + Rule content for general dental coverage explanation
- Recognize question is about "Basic Family Plan" (from PLAN-003 context)
- **Do NOT** state placeholder plan details as facts
- Add disclaimer: "Dental coverage varies by plan. Check your policy documents or contact customer service to confirm whether your Basic Family Plan includes dental benefits."

---

### Scenario 3: Provider Network Question (Placeholder Risk)

**Query:** "Is Dubai Medical Center in-network?"

**Retrieval:**
1. FAQ-015 "How do I find in-network providers?" (Approved)
   - Semantic: 0.85, Weight: 1.0 → **Final: 0.85**
2. NETWORK-001 "Dubai Medical Center [PLACEHOLDER]" (Placeholder)
   - Semantic: 0.98, Weight: 0.2 × 0.8 × 0.5 = 0.08 → **Final: 0.078**

**Result:** FAQ dominates (0.85), Network placeholder heavily downranked (0.078). Answer provides general network verification guidance, does NOT confirm provider status.

**Answer Strategy:**
- Use FAQ content for general network verification guidance
- Recognize question is about "Dubai Medical Center" (from NETWORK-001 context)
- **Do NOT** confirm network status based on placeholder
- Add disclaimer: "To verify whether Dubai Medical Center is in-network for your plan, please check our online provider directory or contact customer service before scheduling your appointment."

---

### Scenario 4: Operational Question (Pending Detail)

**Query:** "How do I refill my prescriptions?"

**Retrieval:**
1. FAQ-011 "How do I refill prescriptions?" (Pending Detail)
   - Semantic: 0.95, Weight: 0.9 × 0.9 = 0.81 → **Final: 0.77**
2. RULE-020 "Pharmacy Benefits" (Active)
   - Semantic: 0.70, Weight: 0.9 → **Final: 0.63**

**Result:** FAQ Pending Detail dominates but with reduced confidence. Answer provides general guidance, defers specifics.

**Answer Strategy:**
- Use FAQ Pending Detail content for general prescription refill guidance
- Add operational disclaimer: "For specific instructions on the refill process covered by your plan, including any mail-order pharmacy options, please contact customer service."
- Reason for disclaimer: Operational details (pharmacy partners, mail-order process) not yet finalized

---

## 8. Weight Tuning and Monitoring

### Initial Weight Configuration

Use weights from this spec as **starting point**:
- FAQ Approved: 1.0
- Rules Active: 0.9
- Mapping High Confidence: 0.6
- Placeholders: 0.2

---

### Monitoring Metrics

**Metric 1: Chunk Type Distribution in Top-10**
- **Target:** FAQ/Rules represent >70% of top-10 results for customer queries
- **Alert:** If placeholders appear in top-10
- **Action:** Increase FAQ/Rules weights or decrease placeholder weights

**Metric 2: Placeholder Ranking**
- **Target:** Placeholders rank below position 20 for customer queries
- **Alert:** If placeholders rank in top-10
- **Action:** Decrease placeholder weights further (e.g., 0.2 → 0.1)

**Metric 3: Answer Quality by Source**
- **Target:** Answers sourced primarily from FAQ (60-70%), Rules (20-30%), Mapping (10%)
- **Alert:** If answers sourced from placeholders
- **Action:** Review filtering and weight configuration

---

### Weight Tuning Process

**Step 1: Collect Baseline Metrics**
- Run sample queries (50-100) across common scenarios
- Record top-10 chunk types and scores
- Measure answer quality (human evaluation)

**Step 2: Identify Issues**
- Placeholders ranking too high? → Decrease placeholder weights
- FAQ not dominating? → Increase FAQ weights or improve FAQ content
- Rules never appearing? → Increase Rules weights

**Step 3: Adjust Weights Incrementally**
- Change weights by 10-20% at a time
- Measure impact on metrics
- Iterate until targets met

**Step 4: Validate**
- Run validation scenarios (see VALIDATION_AND_QA_SPEC.md)
- Ensure placeholder leak rate = 0%
- Ensure answer quality acceptable

---

### Common Weight Tuning Scenarios

**Scenario A: Placeholders Appearing in Top-10**
- **Problem:** Placeholder weights too high OR FAQ weights too low
- **Solution:** Decrease placeholder weights (0.2 → 0.1) AND/OR increase FAQ weights (1.0 → 1.1 if technically feasible, or boost semantically)

**Scenario B: Rules Not Enriching Answers**
- **Problem:** Rules weights too low OR not enough Rules chunks
- **Solution:** Increase Rules weights (0.9 → 1.0) OR add more Rules content

**Scenario C: Mapping Noise**
- **Problem:** Mapping chunks appearing too often in answers
- **Solution:** Ensure Mapping chunks excluded from direct display (filtering), keep weights at 0.4-0.6 for cross-reference only

---

## 9. Implementation Checklist

### Pre-Deployment
- [ ] Retrieval weights stored in metadata (`retrieval_weight_hint`)
- [ ] Status multipliers implemented
- [ ] Use case multipliers defined per use case
- [ ] Weight calculation formula implemented correctly
- [ ] Filtering rules enforce weight thresholds

### Validation
- [ ] FAQ Approved chunks score highest (≥0.85 typical)
- [ ] Placeholder chunks score very low (≤0.2 typical)
- [ ] Trust hierarchy maintained (FAQ > Rules > Mapping > Placeholders)
- [ ] Sample queries tested, top-10 reviewed

### Monitoring
- [ ] Chunk type distribution metrics tracked
- [ ] Placeholder ranking monitored
- [ ] Answer quality measured by source
- [ ] Weight tuning process established

---

## 10. Document Control

**Filename:** RETRIEVAL_WEIGHTING_SPEC.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- METADATA_APPLICATION_SPEC.md - Weight values stored as metadata
- CHUNK_FILTERING_RULES.md - Filtering works with weighting
- PLACEHOLDER_ENFORCEMENT_SPEC.md - Why placeholder weights must be very low

---

**END OF RETRIEVAL WEIGHTING SPECIFICATION**

Apply these weights to ensure FAQ and Rules dominate retrieval, placeholders properly downranked.
