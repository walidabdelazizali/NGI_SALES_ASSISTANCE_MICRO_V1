# Prototype Decision Table (Quick Reference)

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Reference)  

---

## Purpose

This optional reference provides a **quick decision table** for the Phase 1 RAG prototype. Use this for rapid lookup when:
- Classifying queries
- Determining retrieval strategy
- Deciding on disclaimer requirements
- Assessing confidence tiers

For detailed explanations, refer to the full specification documents.

---

## Query Type Decision Table

| Query Type | Keywords/Patterns | Primary Source | Secondary Source | Placeholder Use | Confidence Tier Goal | Disclaimers Required | Caution Level |
|------------|-------------------|---------------|------------------|-----------------|---------------------|---------------------|---------------|
| **1. Conceptual** | "What is...", "Define...", "Explain...", insurance terms | FAQ | Rules | NONE | Tier 1 | NONE (clean) | LOW |
| **2. Policy/Rules** | "Are... covered?", "What are the rules?", policy logic, requirements | Rules + FAQ | Mapping | LOW (if mentioned) | Tier 1-2 | Moderate (if plan-specific) | MODERATE |
| **3. Plan-Specific** | Plan names (Basic Family, Premium Individual, etc.), "Does [plan] cover?" | FAQ + Rules | Plans (context) | **HIGH** (but LOW trust) | **Tier 3** | **MANDATORY** (plan confirmation) | **HIGH** |
| **4. Network-Specific** | Provider names, "in-network", "out-of-network", Dr., hospital, clinic | FAQ + Rules | Network (context) | **HIGH** (but LOW trust) | **Tier 3** | **MANDATORY** (network verification) | **HIGH** |
| **5. Operational** | "How do I...", "Where do I...", process/procedure questions | FAQ | Rules | NONE | Tier 1-2 | Moderate (if Pending Detail) | LOW-MODERATE |
| **6. Mixed** | Multiple types combined (plan + network, plan + benefit, etc.) | FAQ + Rules | Multiple | HIGH | **Tier 3** | **MULTIPLE** mandatory | **HIGH** |
| **7. Unsupported** | Account-specific ("my claim", "my deductible"), off-topic, system operations | NONE | NONE | NONE | **Tier 5** | Fallback message | **SAFE FALLBACK** |

---

## Placeholder Handling Decision Matrix

| Scenario | Placeholder Present? | Placeholder Score After Penalty | Use in Answer? | State Details? | Add Disclaimer? | Confidence Tier |
|----------|---------------------|--------------------------------|---------------|----------------|----------------|-----------------|
| **Conceptual query** ("What is deductible?") | NO | N/A | N/A | N/A | NO | Tier 1 |
| **Policy query** ("Are pre-existing covered?") | NO or LOW | <0.05 (very low) | Context only | NO | Minimal | Tier 1-2 |
| **Plan-specific** ("Does Basic Family Plan cover dental?") | **YES** (plan placeholder) | <0.1 (downweighted) | **CONTEXT ONLY** (recognize name) | ❌ **NEVER** | ✅ **MANDATORY** | **Tier 3** |
| **Network-specific** ("Is Dr. Ahmed in-network?") | **YES** (network placeholder) | <0.1 (downweighted) | **CONTEXT ONLY** (recognize name) | ❌ **NEVER** | ✅ **MANDATORY** | **Tier 3** |
| **Mixed query** (plan + network) | **YES** (both) | <0.1 (downweighted) | **CONTEXT ONLY** | ❌ **NEVER** | ✅ **MULTIPLE** | **Tier 3** |
| **Account-specific** ("What's my claim status?") | NO | N/A | N/A | N/A | Fallback | **Tier 5** |

**Key Rule:** If `is_placeholder=TRUE` and retrieved, **NEVER state details as facts**, ALWAYS add disclaimer, ALWAYS downgrade to Tier 3 or lower.

---

## Disclaimer Decision Table

| Situation | Trigger Condition | Disclaimer Text | Required? | Severity if Missing |
|-----------|------------------|----------------|-----------|---------------------|
| **Plan Confirmation** | Query mentions plan name OR Plans chunk retrieved | "Coverage details vary by plan. Check your policy documents or contact customer service." | ✅ **MANDATORY** | **CRITICAL** |
| **Network Verification** | Query mentions provider/network OR Network chunk retrieved | "Provider network status may vary. Always verify with customer service before scheduling your appointment." | ✅ **MANDATORY** | **CRITICAL** |
| **Placeholder Present** | ANY Plans/Network chunk in results (is_placeholder=TRUE) | "For plan-specific details, check your policy documents or contact customer service at [number]." | ✅ **MANDATORY** | **CRITICAL** |
| **Operational Pending** | FAQ chunk with status="Pending Detail" retrieved | "For complete step-by-step instructions, contact customer service." | ✅ MANDATORY | HIGH |
| **Low Confidence** | Max semantic score <0.6 across all chunks | "This guidance is general. For personalized assistance, contact customer service." | ✅ MANDATORY | HIGH |
| **Compliance/Legal** | Rules chunk with status="Needs Review" AND compliance topic | "This is a compliance matter. For personalized guidance, contact the compliance team or benefits advisor." | ✅ MANDATORY | HIGH |
| **Clean Conceptual** | Tier 1, FAQ-only or FAQ+Rules, high confidence, no placeholders | NONE | ❌ NOT required | N/A |

---

## Confidence Tier Assignment Matrix

| Source Mix | Placeholder Present? | Semantic Match | Assigned Tier | Answer Behavior | Disclaimers |
|------------|---------------------|----------------|---------------|-----------------|-------------|
| FAQ + Rules | NO | High (≥0.7) | **Tier 1** (Strongest) | Confident, direct | Minimal or none |
| FAQ + Rules + Mapping | NO | High (≥0.7) | **Tier 2** (Strong) | Strong, with cross-references | Minimal |
| FAQ + Rules + Placeholder | **YES** | High (≥0.7) | **Tier 3** (Moderate) | Cautious, general guidance | **MANDATORY** |
| Rules-only | NO | Medium (0.5-0.7) | **Tier 4** (Weak) | Weak, policy guidance only | Caution |
| Placeholder-only OR No reliable sources | YES or N/A | Any | **Tier 5** (Unsafe) | **Fallback, refuse certainty** | Fallback message |

**Weakest Link Rule:** Overall confidence = MIN of all source confidences. One weak source downgrades entire answer.

---

## Exclusion Violation Quick Check

| Query Pattern | Prohibited Answer Pattern | Exclusion # | Severity | Safe Alternative |
|---------------|---------------------------|-------------|----------|------------------|
| "Does [Plan] cover [benefit]?" | "Yes, [Plan] covers [benefit] with [%]" | 1 | **CRITICAL** | "Dental coverage varies by plan. For your [Plan]'s specific coverage, check policy documents." |
| "Is [Provider] in-network?" | "Yes, [Provider] is in-network" | 2 | **CRITICAL** | "To verify if [Provider] is in your network, call customer service at [number]." |
| "What's the copay on [Plan]?" | "[Plan] copay is $[amount]" | 3 | **CRITICAL** | "Copay amounts vary by plan. For [Plan]'s specific pricing, contact customer service." |
| "What's my claim status?" | Attempts to provide status | 4 | HIGH | "For account-specific information, log into member portal or contact customer service." |
| "Am I eligible for [plan]?" | Makes eligibility determination | 5 | HIGH | "For enrollment eligibility, contact enrollment services at [number]." |
| "Is this legal?" | Provides binding legal advice | 6 | HIGH | "This is a legal matter. For personalized guidance, consult qualified legal counsel." |
| "Should I get this treatment?" | Recommends medical decisions | 7 | MEDIUM | "For medical advice, consult your healthcare provider." |
| "Update my address to..." | Attempts account operation | 8 | MEDIUM | "To update account information, log into member portal or contact customer service." |
| "Do I need to read my policy?" | "No, this KB is sufficient" | 9 | MEDIUM | "For complete coverage details, your policy documents are the authoritative source." |

---

## Retrieval Strategy Quick Reference

| Query Type | Step 1: FAQ | Step 2: Rules | Step 3: Mapping | Step 4: Placeholder | Final Action |
|------------|-------------|---------------|----------------|---------------------|--------------|
| **Conceptual** | Retrieve top 3-5 | Retrieve top 2-4 (optional) | Optional (context) | ❌ Skip | Generate Tier 1 answer, no disclaimers |
| **Policy/Rules** | Retrieve top 2-3 | Retrieve top 3-5 | Retrieve top 1-3 (cross-links) | Low involvement | Generate Tier 1-2 answer, moderate disclaimers |
| **Plan-Specific** | Retrieve top 3-5 (general guidance) | Retrieve top 2-4 | Optional | **Retrieve top 1-2** (downweighted <0.1, context only) | Generate Tier 3 answer, **mandatory disclaimer**, recognize plan name DON'T state details |
| **Network-Specific** | Retrieve top 3-5 (verification process) | Retrieve top 2-4 | Optional | **Retrieve top 1-2** (downweighted <0.1, context only) | Generate Tier 3 answer, **mandatory verification disclaimer**, recognize provider DON'T confirm status |
| **Operational** | Retrieve top 3-5 | Optional (cross-reference) | Optional | ❌ Skip | Generate Tier 1-2 answer, check for Pending Detail |
| **Unsupported** | Attempt retrieval (likely low match) | Attempt retrieval (likely low match) | Skip | ❌ Skip | **Tier 5 fallback**, direct to appropriate resources |

---

## Answer Generation Strategy Matrix

| Confidence Tier | Source Mix | Answer Structure | Tone | Disclaimers | Example Output Length |
|----------------|------------|------------------|------|-------------|-----------------------|
| **Tier 1** | FAQ + Rules (strong) | Direct answer → Supporting detail → Example | Confident, friendly | None or minimal | 2-3 paragraphs |
| **Tier 2** | FAQ + Rules + Mapping | Direct answer → Supporting detail → Related topics | Strong, informative | Minimal | 2-4 paragraphs |
| **Tier 3** | + Placeholder present | General guidance → Verification steps → **Disclaimer** | Cautious, helpful | **MANDATORY** | 3-4 paragraphs + disclaimer |
| **Tier 4** | Rules-only or low conf | Policy guidance → Caution → Contact info | Weak, careful | Caution | 1-2 paragraphs + disclaimer |
| **Tier 5** | Placeholder-only or none | Safe fallback → Direct to resources | Honest, helpful | Fallback message | 1 paragraph fallback |

---

## Safety Rules Quick Checklist

**Before Generating Answer:**
- [ ] Calculate confidence tier (weakest link rule)
- [ ] Check if placeholder present → Downgrade to Tier 3
- [ ] Determine mandatory disclaimers (6 situations)
- [ ] Check exclusion violations (9 exclusions)

**After Generating Answer:**
- [ ] Verify NO placeholder details stated as facts
- [ ] Verify mandatory disclaimers present if required
- [ ] Verify no inappropriate operations attempted
- [ ] Attach full traceability metadata

**Never Allow:**
- ❌ Placeholder benefits, network status, or costs stated as facts
- ❌ Missing plan confirmation or network verification disclaimers
- ❌ Claims adjudication, underwriting, account operations
- ❌ Overconfident answers when placeholders present

---

## Common Query Examples with Expected Behavior

| Query | Type | Primary Source | Confidence Tier | Disclaimers | Key Points |
|-------|------|---------------|-----------------|-------------|-----------|
| "What is a deductible?" | Conceptual | FAQ-001 | Tier 1 | None | Clean, confident answer |
| "Are pre-existing conditions covered?" | Policy | FAQ-008 + RULE-007 | Tier 1-2 | Minimal | Policy explanation + disclosure requirement |
| "Does Basic Family Plan cover dental?" | Plan-Specific | FAQ-005 + PLAN-003 (context) | **Tier 3** | **MANDATORY** | General guidance, recognize plan name, DON'T state details |
| "Is Dr. Ahmed in-network?" | Network-Specific | FAQ-015 + PROV-002 (context) | **Tier 3** | **MANDATORY** | Verification process, recognize provider, DON'T confirm status |
| "How do I file a claim?" | Operational | FAQ-009 | Tier 1-2 | Minimal | Step-by-step process |
| "What's my claim status?" | Account-Specific | NONE | **Tier 5** | Fallback | Direct to portal/customer service |
| "Does Basic Family Plan cover Dr. Ahmed for maternity?" | Mixed | FAQ-007 + FAQ-015 + PLAN-003 + PROV-002 | **Tier 3** | **MULTIPLE** | Multiple disclaimers, general guidance for all aspects |

---

## Implementation Quick Reference

### Core Algorithm (Simplified)

```
1. NORMALIZE query (lowercase, extract entities)

2. RETRIEVE chunks:
   - FAQ: top 3-5, weight 1.0
   - Rules: top 2-4, weight 0.9
   - Mapping: top 1-3, weight 0.5
   - Placeholder: if plan/network query, top 1-2, weight 0.2 × penalty 0.08

3. CALCULATE tier:
   - Placeholder present? → Tier 3 (or lower)
   - FAQ + Rules, high semantic? → Tier 1
   - Placeholder-only or low semantic? → Tier 5
   - Apply weakest link rule

4. DETERMINE disclaimers:
   - Plan name mentioned? → MANDATORY plan disclaimer
   - Network keyword? → MANDATORY network disclaimer
   - Placeholder present? → MANDATORY placeholder disclaimer
   - (Check all 6 situations)

5. CHECK violations:
   - Placeholder details in answer? → BLOCK (CRITICAL)
   - Network status confirmed? → BLOCK (CRITICAL)
   - Cost from placeholder? → BLOCK (CRITICAL)
   - (Check all 9 exclusions)

6. GENERATE answer by tier:
   - Tier 1: Confident, no disclaimers
   - Tier 3: Cautious, mandatory disclaimers
   - Tier 5: Safe fallback

7. ATTACH metadata:
   - Source chunks (all metadata)
   - Answer metadata (tier, disclaimers, safety rules)
   - Performance metrics
```

---

## When to Use This Table

**Use this decision table for:**
- ✅ Quick query classification during testing
- ✅ Rapid disclaimer requirement checks
- ✅ Confidence tier validation
- ✅ Placeholder handling decisions
- ✅ Safety rule quick reference

**Do NOT use as replacement for:**
- ❌ Full specification documents (refer to detailed specs for implementation)
- ❌ Safety rule implementation (implement ALL 9 exclusions from PROTOTYPE_EXCLUSIONS.md)
- ❌ Testing validation (use PROTOTYPE_TEST_QUERIES.md full test set)

---

## Document Control

**Filename:** PROTOTYPE_DECISION_TABLE.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Reference)  

**Related Documents:**
- PROTOTYPE_QUERY_HANDLING.md - Detailed query type strategies
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Full answer generation rules
- PROTOTYPE_EXCLUSIONS.md - Complete exclusion specifications
- PROTOTYPE_RETRIEVAL_FLOW.md - Detailed retrieval process
- SAMPLE_QUERY_TO_CHUNK_PATHS.md - Worked examples

---

**END OF DECISION TABLE**
