# Chunk Priority Matrix - Micro Insurance KB V1

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Rank chunk types by ingestion priority, retrieval confidence, and safety criteria

---

## 1. Master Priority Matrix

| Chunk Type | Ingestion Priority | Retrieval Confidence | Direct Customer Use | Verification Need | Retrieval Weight | Phase |
|------------|-------------------|---------------------|---------------------|------------------|------------------|-------|
| **FAQ (Approved)** | 🟢 Critical | 🟢 High | ✅ Safe | Low | 1.0 | Phase 1 |
| **FAQ (Needs Review)** | 🟡 High | 🟡 Medium-High | ⚠️ Caution | Medium | 0.95 | Phase 1 |
| **FAQ (Pending Detail)** | 🟡 High | 🟡 Medium | ⚠️ Caution | High | 0.9 | Phase 1 |
| **Rules (Active)** | 🟢 Critical | 🟢 High | ✅ Safe | Low | 0.9 | Phase 1 |
| **Rules (Needs Review)** | 🟡 High | 🟡 Medium | ⚠️ Caution | Medium | 0.85 | Phase 1 |
| **Mapping (High Conf)** | 🟡 High | 🟡 Medium | ❌ Reference Only | Low | 0.6 | Phase 1 |
| **Mapping (Medium Conf)** | 🟡 High | 🟡 Medium | ❌ Reference Only | Medium | 0.5 | Phase 1 |
| **Mapping (Low Conf)** | 🟠 Medium | 🟠 Low-Medium | ❌ Reference Only | High | 0.4 | Phase 1 |
| **Plans (Placeholder)** | 🔴 Low | 🔴 Very Low | ❌ Unsafe | Very High | 0.2 | Phase 2 |
| **Network (Placeholder)** | 🔴 Low | 🔴 Very Low | ❌ Unsafe | Very High | 0.2 | Phase 2 |

---

## 2. Priority Scale Definitions

### Ingestion Priority

| Level | Description | Recommendation |
|-------|-------------|----------------|
| 🟢 **Critical** | Essential for core functionality | Ingest immediately (Phase 1) |
| 🟡 **High** | Important for complete knowledge | Ingest in Phase 1 |
| 🟠 **Medium** | Useful but not essential | Ingest in Phase 1 with caution |
| 🔴 **Low** | Structural/placeholder only | Ingest in Phase 2 with strict guardrails |

### Retrieval Confidence

| Level | Description | Certainty | Usage |
|-------|-------------|-----------|-------|
| 🟢 **High** | Approved, verified content | 90-100% | Can answer customer questions directly |
| 🟡 **Medium-High** | Reviewed but not finalized | 70-90% | Can use with light disclaimer |
| 🟡 **Medium** | Partial information or review needed | 50-70% | Use with disclaimer, defer details |
| 🟠 **Low-Medium** | Provisional or low-confidence links | 30-50% | Use cautiously, add strong disclaimer |
| 🔴 **Very Low** | Placeholder, unverified | 0-30% | Routing only, never present as fact |

### Direct Customer Use Safety

| Rating | Description | Guardrail Requirement |
|--------|-------------|----------------------|
| ✅ **Safe** | Can be presented to customers directly | No special disclaimer required |
| ⚠️ **Caution** | Can be used with appropriate disclaimers | Add verification disclaimer |
| ❌ **Reference Only** | Internal system use, not for customer display | Do not show mapping text to customers |
| ❌ **Unsafe** | Never present as confirmed fact | Filter or add strong verification disclaimer |

### Verification Need

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **Low** | Content is approved and reliable | Can use confidently |
| **Medium** | Content needs review or additional context | Add light disclaimer |
| **High** | Content has known gaps or requires external verification | Add strong disclaimer, defer to customer service |
| **Very High** | Content is placeholder or unverified | Must verify with authoritative source, never state as fact |

---

## 3. Chunk Type Deep Dive

### FAQ Chunks (Approved)

**Priority Ranking:** 🟢 1st - Critical  
**Confidence:** High (90-100%)  
**Count:** 9 chunks

**Characteristics:**
- Status: Approved
- Content: Training-derived, hardened, reviewed
- Use Case: Primary retrieval for customer questions
- Risk: Low

**Retrieval Strategy:**
- Direct customer answers ✅
- No disclaimer required for general guidance
- Add disclaimer only if plan-specific or network-specific truth required

**Weight:** 1.0 (full strength)

**Ingestion:** Phase 1, highest priority

---

### FAQ Chunks (Needs Review)

**Priority Ranking:** 🟡 2nd - High  
**Confidence:** Medium-High (70-90%)  
**Count:** 7 chunks

**Characteristics:**
- Status: Needs Review
- Content: Training-derived, hardened, requires final review
- Use Case: Can answer customer questions with caution
- Risk: Low-Medium

**Retrieval Strategy:**
- Can use for customer answers ✅
- Add light disclaimer: "Please verify with customer service if critical"
- Monitor for accuracy issues

**Weight:** 0.95 (near full strength)

**Ingestion:** Phase 1, high priority

---

### FAQ Chunks (Pending Detail)

**Priority Ranking:** 🟡 3rd - High (but use with caution)  
**Confidence:** Medium (50-70%)  
**Count:** 4 chunks

**Characteristics:**
- Status: Pending Detail
- Content: Generic guidance, lacks operational specifics
- Use Case: General guidance only, defer details to customer service
- Risk: Medium

**Retrieval Strategy:**
- Can provide general context ⚠️
- Must add disclaimer about contacting customer service for specifics
- Cannot provide step-by-step operational instructions

**Weight:** 0.9 (reduced strength)

**Ingestion:** Phase 1, but flag for future enhancement

**Affected FAQs:**
- FAQ-011: Prescription refills (process undefined)
- FAQ-013: Insurance card access (delivery process undefined)
- FAQ-017: Contact support (channels undefined)
- FAQ-020: Change doctor/hospital (flexibility rules undefined)

---

### Rules Chunks (Active)

**Priority Ranking:** 🟢 1st - Critical  
**Confidence:** High (90-100%)  
**Count:** 26 chunks

**Characteristics:**
- Status: Active
- Content: Generic insurance business logic, broadly applicable
- Use Case: Support FAQ answers with detailed reasoning
- Risk: Low

**Retrieval Strategy:**
- Use for reasoning and explanation ✅
- Can reference `client_safe_summary` in customer answers
- Use `internal_usage_note` for system reasoning only (not customer-facing)

**Weight:** 0.9 (high strength, slightly below FAQ for user queries)

**Ingestion:** Phase 1, highest priority

---

### Rules Chunks (Needs Review)

**Priority Ranking:** 🟡 4th - High  
**Confidence:** Medium (60-80%)  
**Count:** 1 chunk (RULE-008: Pre-existing Non-Disclosure Review)

**Characteristics:**
- Status: Needs Review
- Content: Softened from harsh original language, requires compliance check
- Use Case: Can reference cautiously
- Risk: Medium (legal/compliance sensitive)

**Retrieval Strategy:**
- Can use for general reasoning ⚠️
- Add disclaimer if referencing consequences
- Prioritize compliance review

**Weight:** 0.85 (reduced for review status)

**Ingestion:** Phase 1, but flag for compliance review

---

### Mapping Chunks (High Confidence)

**Priority Ranking:** 🟡 5th - High  
**Confidence:** Medium (60-80%)  
**Count:** 16 chunks (estimated - confidence field not on all)

**Characteristics:**
- Confidence: High
- Content: FAQ-to-rule links, well-established relationships
- Use Case: Cross-reference enrichment, context retrieval
- Risk: Low

**Retrieval Strategy:**
- Use to enrich FAQ context ✅
- Retrieve linked rules confidently
- Do not display mapping text to customers (use linked content instead)

**Weight:** 0.6 (medium - reference layer, not primary content)

**Ingestion:** Phase 1, important for cross-linking

---

### Mapping Chunks (Medium Confidence)

**Priority Ranking:** 🟡 6th - High  
**Confidence:** Medium (50-70%)  
**Count:** ~1 chunk (estimated)

**Characteristics:**
- Confidence: Medium
- Content: FAQ-to-rule links, reasonable but not fully verified relationships
- Use Case: Cross-reference with caution
- Risk: Medium

**Retrieval Strategy:**
- Can enrich FAQ context ⚠️
- Retrieve linked rules but add disclaimer if answer depends heavily on link
- Monitor retrieval quality

**Weight:** 0.5 (medium)

**Ingestion:** Phase 1, but monitor for accuracy

---

### Mapping Chunks (Low Confidence)

**Priority Ranking:** 🟠 7th - Medium  
**Confidence:** Low-Medium (30-50%)  
**Count:** 3 chunks (MAP-012, MAP-013, MAP-017)

**Characteristics:**
- Confidence: Low
- Content: Operational/technical FAQs mapped to tangentially related rules (provisional)
- Use Case: Lightweight context, not reliable for final answers
- Risk: Medium-High

**Retrieval Strategy:**
- Use for routing awareness only ⚠️
- Linked rules may not fully address the FAQ
- Add strong disclaimer: "General guidance. Contact customer service for specifics."

**Weight:** 0.4 (low-medium - downweighted for low confidence)

**Ingestion:** Phase 1, but flag as provisional

**Affected Mappings:**
- MAP-012: Login issues → RULE-016 (Terms acceptance) - tangential
- MAP-013: Insurance card access → RULE-023 (Benefit confirmation) - loosely related
- MAP-017: Contact support → RULE-027 (Generic support statement) - generic

---

### Plans Chunks (ALL Placeholder)

**Priority Ranking:** 🔴 8th - Low (ingest last)  
**Confidence:** Very Low (0-20%)  
**Count:** 10 chunks (ALL placeholder)

**Characteristics:**
- Status: Pending Detail (100%)
- is_placeholder: true (100%)
- Content: Structural scaffolding, NOT confirmed product definitions
- Use Case: Structural awareness, routing only
- Risk: **VERY HIGH** - easily misinterpreted as real benefits

**Retrieval Strategy:**
- **DO NOT** use for customer answers ❌
- **DO NOT** present as confirmed plan benefits ❌
- Can use for internal routing: "This sounds like a plan-specific question"
- Can identify plan type context
- **MUST** add strong disclaimer if referenced at all

**Weight:** 0.2 (very low - minimal retrieval influence)

**Ingestion:** Phase 2 only, with strict guardrails

**Critical Warning:**
```
⚠️ NEVER state placeholder plan data as fact.
   Always add: "Check your policy documents for your specific plan benefits."
```

---

### Network Chunks (ALL Placeholder)

**Priority Ranking:** 🔴 9th - Low (ingest last)  
**Confidence:** Very Low (0-20%)  
**Count:** 10 chunks (ALL placeholder)

**Characteristics:**
- Status: Pending Detail (100%)
- is_placeholder: true (100%)
- Content: Structural scaffolding, NOT live provider directory
- Use Case: Provider type awareness, routing only
- Risk: **VERY HIGH** - easily misinterpreted as verified provider data

**Retrieval Strategy:**
- **DO NOT** use for customer answers ❌
- **DO NOT** confirm provider network status ❌
- Can use for internal routing: "This sounds like a network/provider question"
- Can identify provider type context
- **MUST** add strong disclaimer if referenced at all

**Weight:** 0.2 (very low - minimal retrieval influence)

**Ingestion:** Phase 2 only, with strict guardrails

**Critical Warning:**
```
⚠️ NEVER state placeholder network data as fact.
   Always add: "Verify provider network status with customer service."
```

---

## 4. Ingestion Order Recommendation

### Phase 1 (Priority Ingestion)

```
Step 1: FAQ Chunks (Approved) ─────────► 9 chunks, highest confidence
Step 2: Rules Chunks (Active) ─────────► 26 chunks, high confidence
Step 3: FAQ Chunks (Needs Review) ─────► 7 chunks, medium-high confidence
Step 4: FAQ Chunks (Pending Detail) ───► 4 chunks, medium confidence, use cautiously
Step 5: Rules Chunks (Needs Review) ───► 1 chunk, medium confidence
Step 6: Mapping Chunks (All) ──────────► 20 chunks, varying confidence

Total Phase 1: 67 chunks
```

**Outcome:** Strong knowledge base for customer Q&A and reasoning.

---

### Phase 2 (Placeholder Ingestion with Guardrails)

```
Step 7: Plans Chunks ──────────────────► 10 placeholder chunks, very low confidence
Step 8: Network Chunks ────────────────► 10 placeholder chunks, very low confidence

Total Phase 2: 20 chunks
```

**Outcome:** Structural awareness for routing, NOT for customer answers.

---

## 5. Retrieval Weight Summary

### Production Retrieval Weights

| Chunk Type | Weight | Rationale |
|------------|--------|-----------|
| FAQ (Approved) | 1.0 | Highest priority for customer questions |
| FAQ (Needs Review) | 0.95 | Near-approved, use with light caution |
| FAQ (Pending Detail) | 0.9 | Useful but incomplete, defer details |
| Rules (Active) | 0.9 | High-quality reasoning, strong for logic |
| Rules (Needs Review) | 0.85 | Needs compliance check, use cautiously |
| Mapping (High Confidence) | 0.6 | Reference layer, not primary content |
| Mapping (Medium Confidence) | 0.5 | Lower certainty, monitor quality |
| Mapping (Low Confidence) | 0.4 | Provisional links, use with disclaimer |
| Plans (Placeholder) | 0.2 | Structural only, not for answers |
| Network (Placeholder) | 0.2 | Structural only, not for answers |

**Implementation Note:** Apply weight as multiplier to semantic similarity score.

```python
final_score = semantic_similarity * retrieval_weight_hint
```

---

## 6. Risk Assessment Matrix

### Risk by Chunk Type

| Chunk Type | Legal Risk | Customer Misinformation Risk | Regulatory Risk | Overall Risk |
|------------|-----------|------------------------------|-----------------|--------------|
| FAQ (Approved) | 🟢 Low | 🟢 Low | 🟢 Low | 🟢 Low |
| FAQ (Needs Review) | 🟡 Medium | 🟡 Medium | 🟢 Low | 🟡 Medium |
| FAQ (Pending Detail) | 🟡 Medium | 🟡 Medium | 🟡 Medium | 🟡 Medium |
| Rules (Active) | 🟢 Low | 🟢 Low | 🟢 Low | 🟢 Low |
| Rules (Needs Review) | 🟡 Medium | 🟡 Medium | 🟡 Medium | 🟡 Medium |
| Mapping (Any) | 🟢 Low | 🟢 Low | 🟢 Low | 🟢 Low |
| Plans (Placeholder) | 🔴 High | 🔴 High | 🔴 High | 🔴 High |
| Network (Placeholder) | 🔴 High | 🔴 High | 🔴 High | 🔴 High |

**Mitigation:** Apply guardrails per RETRIEVAL_GUARDRAILS.md

---

## 7. Usage Recommendations by Use Case

### Customer-Facing Chatbot

**Include:**
- FAQ (Approved) ✅ - Full confidence
- Rules (Active) ✅ - For reasoning
- Mapping (High/Medium) ✅ - For context enrichment

**Include with Disclaimers:**
- FAQ (Needs Review) ⚠️ - Light disclaimer
- FAQ (Pending Detail) ⚠️ - Defer to customer service for details

**Exclude or Heavily Disclaim:**
- Plans (Placeholder) ❌ - Never present as fact
- Network (Placeholder) ❌ - Never present as fact
- Mapping (Low Confidence) ⚠️ - Use cautiously

---

### Internal Knowledge Assistant

**Include:**
- All FAQ chunks ✅
- All Rules chunks ✅
- All Mapping chunks ✅

**Include with Warnings:**
- Plans (Placeholder) ⚠️ - Flag as placeholder
- Network (Placeholder) ⚠️ - Flag as placeholder

---

### Customer Self-Service FAQ Page

**Include:**
- FAQ (Approved) only ✅
- Rules (Active) for reasoning ✅

**Exclude:**
- Everything else (too much risk for unguided self-service)

---

## 8. Success Metrics by Priority Tier

### Tier 1 (Phase 1 Strong Knowledge)

**Target Metrics:**
- Retrieval relevance: >85% for common questions
- Answer accuracy: >90%
- Customer satisfaction: >4.0/5.0
- Placeholder leak rate: 0%

### Tier 2 (Phase 2 Placeholder Knowledge)

**Target Metrics:**
- Placeholder filter effectiveness: 100% (no leaks to customer answers)
- Disclaimer compliance: 100% (all plan/network answers have disclaimers)
- Routing accuracy: >70% (correctly identifies plan/network questions)

---

## 9. Priority Matrix Visualization

```
High Confidence, High Priority (INGEST FIRST):
┌─────────────────────────────────────────┐
│ FAQ (Approved)        [Priority: 1]     │ ← CRITICAL
│ Rules (Active)        [Priority: 1]     │ ← CRITICAL
└─────────────────────────────────────────┘

Medium-High Confidence, High Priority:
┌─────────────────────────────────────────┐
│ FAQ (Needs Review)    [Priority: 2]     │
│ FAQ (Pending Detail)  [Priority: 3]     │
│ Rules (Needs Review)  [Priority: 4]     │
└─────────────────────────────────────────┘

Medium Confidence, Reference Layer:
┌─────────────────────────────────────────┐
│ Mapping (High Conf)   [Priority: 5]     │
│ Mapping (Med Conf)    [Priority: 6]     │
│ Mapping (Low Conf)    [Priority: 7]     │
└─────────────────────────────────────────┘

Low Confidence, Placeholder (INGEST LAST WITH GUARDRAILS):
┌─────────────────────────────────────────┐
│ Plans (Placeholder)   [Priority: 8]     │ ⚠️ HIGH RISK
│ Network (Placeholder) [Priority: 9]     │ ⚠️ HIGH RISK
└─────────────────────────────────────────┘
```

---

## 10. Decision Tree: Should I Use This Chunk?

```
Is this chunk for a customer-facing answer?
├─ YES
│  ├─ Is is_placeholder = true?
│  │  ├─ YES → ❌ DO NOT USE or add strong verification disclaimer
│  │  └─ NO → Continue...
│  ├─ Is status = "Approved" or "Active"?
│  │  ├─ YES → ✅ SAFE TO USE
│  │  └─ NO → Continue...
│  ├─ Is status = "Needs Review"?
│  │  ├─ YES → ⚠️ USE WITH LIGHT DISCLAIMER
│  │  └─ NO → Continue...
│  ├─ Is status = "Pending Detail"?
│  │  ├─ YES → ⚠️ GENERIC GUIDANCE ONLY, defer details to customer service
│  │  └─ NO → ❌ Unknown status, do not use
│
└─ NO (internal use only)
   └─ ✅ CAN USE with appropriate caution based on confidence
```

---

## 11. Summary: Priority Ranking (1-9)

1. 🥇 **FAQ (Approved) + Rules (Active)** - Critical, high confidence, ingest first
2. 🥈 **FAQ (Needs Review)** - High priority, medium-high confidence, use with light caution
3. 🥉 **FAQ (Pending Detail) + Rules (Needs Review)** - High priority, medium confidence, defer details
4. **Mapping (High/Medium)** - Important for cross-reference, medium confidence
5. **Mapping (Low Confidence)** - Use cautiously, provisional links
6. 🚫 **Plans (Placeholder)** - Low priority, very low confidence, ingest last, strict guardrails
7. 🚫 **Network (Placeholder)** - Low priority, very low confidence, ingest last, strict guardrails

---

**End of Chunk Priority Matrix**

✅ **Use this matrix to prioritize ingestion and retrieval strategies**  
⚠️ **Remember: Placeholder content requires strict guardrails**
