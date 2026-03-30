# Answer Safety Behavior Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define answer generation behavior based on retrieved chunk mix

---

## 1. Overview

This specification defines **answer safety behavior** based on the **MIX of retrieved chunks**, not individual chunks. Answer confidence and required disclaimers depend on the **weakest link** in the retrieval chain.

### Core Principle: Weakest Link Rule

**Answer overall confidence = MIN(confidence of all chunks in chain)**

If any retrieved chunk is low-confidence, placeholder, or requires verification, the ENTIRE answer inherits appropriate safety behavior.

---

## 2. Retrieval Scenario Classification

### Scenario 1: FAQ + Rule only (STRONGEST)
**Retrieved Chunks:** FAQ (Approved/Needs Review) + Rule (Active)  
**Confidence:** HIGH  
**Safety:** Safe for direct customer use  

---

### Scenario 2: FAQ + Rule + Mapping (STRONG)
**Retrieved Chunks:** FAQ + Rule + Mapping (enrichment)  
**Confidence:** HIGH  
**Safety:** Safe for direct customer use (mapping used for context, not displayed directly)  

---

### Scenario 3: FAQ + Rule + Plan Placeholder (MODERATE with CAUTION)
**Retrieved Chunks:** FAQ + Rule + placeholder  
**Confidence:** MODERATE  
**Safety:** Provide FAQ/Rule content, acknowledge plan-specific nature, require disclaimer  

---

### Scenario 4: FAQ + Rule + Network Placeholder (MODERATE with CAUTION)
**Retrieved Chunks:** FAQ + Rule + placeholder  
**Confidence:** MODERATE  
**Safety:** Provide FAQ/Rule content, require network verification disclaimer  

---

### Scenario 5: Rule-only (MODERATE)
**Retrieved Chunks:** Rule only (no FAQ match)  
**Confidence:** MODERATE  
**Safety:** Provide policy reasoning, acknowledge limited direct FAQ coverage  

---

### Scenario 6: Placeholder-only (UNSAFE - Should Not Happen)
**Retrieved Chunks:** Only placeholders (no FAQ or Rule match)  
**Confidence:** VERY LOW  
**Safety:** UNSAFE - Defer to customer service immediately  

---

### Scenario 7: Conflicting or Low-Confidence (CAUTIOUS)
**Retrieved Chunks:** Multiple chunks with conflicting info or all Needs Review/Pending Detail  
**Confidence:** LOW  
**Safety:** Provide general guidance only, require verification  

---

## 3. Detailed Answer Behavior by Scenario

---

## SCENARIO 1: FAQ + Rule Only (STRONGEST)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. FAQ-001 (weight 1.0, status Approved, is_placeholder false)
2. RULE-001 (weight 0.9, status Active, is_placeholder false)
```

### Answer Behavior

**Allowed Answer Style:**
- Confident, direct answer
- Provide specific guidance from FAQ
- Enriched with policy reasoning from Rule
- No disclaimers needed (unless operational in nature)

**Example Query:** "What is a deductible?"

**Retrieved:**
- FAQ-001: Deductible explanation (Approved)
- RULE-001: Deductible calculation rules (Active)

**Generated Answer:**
```
A deductible is the amount you pay out-of-pocket before your insurance coverage begins. 

For example, if your plan has a deductible of AED 500, you'll pay the first AED 500 
of covered medical expenses yourself. After you meet your deductible, your insurance 
starts covering expenses according to your plan benefits.

Your deductible typically resets annually at the start of your policy year.
```

**Why Safe:**
- Both sources are high-confidence (FAQ Approved + Rule Active)
- No placeholder content
- FAQ provides customer-friendly explanation
- Rule provides policy context
- No plan-specific or network-specific claims

**Required Disclaimers:** None (general insurance concept)

---

## SCENARIO 2: FAQ + Rule + Mapping (STRONG)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. FAQ-005 (weight 1.0, status Approved)
2. RULE-003 (weight 0.9, status Active)
3. MAP-005 (weight 0.6, links FAQ-005 to RULE-003 and PLAN-003)
```

### Answer Behavior

**Allowed Answer Style:**
- Confident answer from FAQ + Rule
- Use mapping for context (find related chunks)
- Do NOT display mapping text directly to customer
- Acknowledge plan-specific nature if mapping indicates it

**Example Query:** "Does my plan cover dental?"

**Retrieved:**
- FAQ-005: General dental coverage explanation
- RULE-003: Benefit categories
- MAP-005: Links FAQ to rules and notes "requires plan confirmation"

**Generated Answer:**
```
Dental coverage varies by plan. Many plans include coverage for preventive 
dental care (cleanings, exams) and may include coverage for basic procedures 
like fillings.

[From Rule context: Dental benefits are categorized as optional or supplemental 
depending on plan type.]

To confirm your specific dental coverage and benefit limits, please check your 
policy documents or contact customer service at [number].
```

**Why Safe:**
- FAQ and Rule provide general guidance (high confidence)
- Mapping signals "requires plan confirmation" (used to trigger disclaimer)
- Mapping text not shown directly (reference layer)
- Plan-specific details deferred to authoritative sources

**Required Disclaimers:**
- ✅ "Check your policy documents for plan-specific details"
- ✅ Related plan identified from mapping: defers confirmation

---

## SCENARIO 3: FAQ + Rule + Plan Placeholder (MODERATE with CAUTION)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. FAQ-005 (weight 1.0, status Approved, is_placeholder false)
2. RULE-003 (weight 0.9, status Active, is_placeholder false)
3. MAP-005 (weight 0.6)
4. PLAN-003 (weight 0.08, status Pending Detail, is_placeholder true) ← Placeholder!
```

### Answer Behavior

**Allowed Answer Style:**
- Provide FAQ + Rule content (high confidence)
- Recognize plan name from placeholder (context awareness)
- DO NOT state placeholder details as facts
- MANDATORY disclaimer: defer to policy documents

**Example Query:** "Does my Basic Family Plan cover dental?"

**Retrieved:**
- FAQ-005: General dental coverage
- RULE-003: Benefit categories
- PLAN-003: Basic Family Plan placeholder (is_placeholder true)

**Generated Answer:**
```
Dental coverage varies by plan type and tier. Many plans include preventive 
dental care (cleanings, exams), and some plans include additional coverage 
for basic and major procedures.

For specific dental coverage details for your Basic Family Plan, please:
- Check your policy documents or benefits summary
- Contact customer service at [number]
- Log into your member portal

I can help you understand general dental coverage concepts like preventive 
vs. major care, benefit limits, and provider networks.
```

**Why Safe:**
- General content from FAQ + Rule (high confidence)
- Placeholder used only for context awareness ("Basic Family Plan" recognized)
- NO placeholder details stated as facts (no cost, no coverage confirmation)
- Strong disclaimer redirects to authoritative sources

**Required Disclaimers:**
- ✅ "Check your policy documents for plan-specific details"
- ✅ Defer to customer service/member portal
- ❌ Do NOT state: "Basic Family Plan covers X" (placeholder not confirmed)

**Forbidden:**
- ❌ "Your Basic Family Plan covers dental cleanings twice per year" (placeholder as fact)
- ❌ "Your deductible is AED 500" (placeholder cost)
- ❌ Comparing Basic Family Plan to other placeholders

---

## SCENARIO 4: FAQ + Rule + Network Placeholder (MODERATE with CAUTION)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. FAQ-015 (weight 1.0, status Approved, is_placeholder false)
2. RULE-015 (weight 0.9, status Active, is_placeholder false)
3. PROV-001 (weight 0.08, status Pending Detail, is_placeholder true) ← Network Placeholder!
```

### Answer Behavior

**Allowed Answer Style:**
- Provide FAQ + Rule guidance on network verification
- Recognize provider/hospital name from placeholder (context awareness)
- DO NOT confirm in-network status
- MANDATORY disclaimer: verify provider network status

**Example Query:** "Is Dubai Medical Center in-network?"

**Retrieved:**
- FAQ-015: How to verify provider network status
- RULE-015: Network participation rules
- PROV-001: Dubai Medical Center placeholder (is_placeholder true)

**Generated Answer:**
```
To verify whether Dubai Medical Center is in-network for your plan:

1. Check our online provider directory at [URL]
2. Contact customer service at [number] with the provider name
3. Ask the provider's billing office to verify your insurance acceptance

Provider network participation can change, so it's important to verify before 
scheduling your appointment to ensure you receive in-network benefits.
```

**Why Safe:**
- General network verification process from FAQ + Rule (high confidence)
- Placeholder used only to recognize "Dubai Medical Center" (context awareness)
- NO confirmation of network status (placeholder not verified)
- Strong disclaimer: verify before appointment

**Required Disclaimers:**
- ✅ "Verify provider network status before scheduling appointment"
- ✅ "Provider network participation can change"
- ❌ Do NOT state: "Dubai Medical Center is in-network" (placeholder not verified)

**Forbidden:**
- ❌ "Yes, Dubai Medical Center is in our Premium Network" (placeholder as fact)
- ❌ "Dubai Medical Center accepts all our plans" (placeholder generalization)
- ❌ Recommending provider based on placeholder data

---

## SCENARIO 5: Rule-Only (MODERATE)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. RULE-008 (weight 0.85, status Needs Review)
[No FAQ match - specialized policy question]
```

### Answer Behavior

**Allowed Answer Style:**
- Provide policy reasoning from Rule
- Acknowledge this is policy-level guidance (not customer FAQ)
- If Rule is "Needs Review", add caution disclaimer

**Example Query:** "What happens if I don't disclose a pre-existing condition?"

**Retrieved:**
- RULE-008: Pre-existing Condition Non-Disclosure Review (Needs Review status)

**Generated Answer:**
```
Regarding policy requirements for pre-existing condition disclosure:

[Policy-level guidance from RULE-008]

This is a compliance and policy matter. For specific guidance about your situation:
- Contact customer service at [number]
- Consult your policy documents
- Speak with our compliance team if needed

Note: Policy interpretation may vary depending on circumstances. It's important 
to get personalized guidance.
```

**Why Safe:**
- Rule provides policy reasoning (moderate confidence)
- "Needs Review" status acknowledged with caution
- No customer-friendly FAQ available (acknowledged in answer)
- Defers complex policy interpretation to specialists

**Required Disclaimers:**
- ✅ "Policy interpretation may vary, contact customer service"
- ✅ If Needs Review: "For specific guidance, consult compliance team"

---

## SCENARIO 6: Placeholder-Only (UNSAFE - Should Not Happen)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. PLAN-003 (weight 0.08, is_placeholder true)
2. PLAN-005 (weight 0.07, is_placeholder true)
[No FAQ or Rule match]
```

### Answer Behavior

**This scenario should NOT happen** if filtering is correctly implemented. Customer-facing retrieval should exclude `is_placeholder: true`.

**If it happens (system failure):**

**Generated Answer:**
```
I don't have reliable information to answer that question accurately. 

For accurate information about your plan, please contact customer service at 
[number] or visit our website at [URL].

Our team can provide specific details about your coverage, benefits, and costs.
```

**Why Safe:**
- Honest acknowledgment of limitation
- NO attempt to use placeholder content
- Immediate redirect to authoritative sources
- Avoids legal liability

**Required Actions:**
- ✅ Generate safe fallback answer
- ✅ Log incident (placeholder leak detection)
- ✅ Alert engineering team (filtering failure)
- ✅ Investigate root cause

**Forbidden:**
- ❌ Use placeholder content as if real
- ❌ Attempt to answer using placeholder details
- ❌ Compare placeholder plans

---

## SCENARIO 7: Conflicting or Low-Confidence (CAUTIOUS)

### Retrieval Pattern
```
Top Retrieved Chunks:
1. FAQ-011 (weight 0.81, status Pending Detail)
2. FAQ-017 (weight 0.81, status Pending Detail)
3. RULE-020 (weight 0.9, status Active)
[Multiple Pending Detail chunks OR conflicting information]
```

### Answer Behavior

**Allowed Answer Style:**
- Provide general guidance (avoid specifics)
- Acknowledge operational nature (if applicable)
- Strong disclaimer: defer to customer service for specifics

**Example Query:** "How do I refill a prescription?"

**Retrieved:**
- FAQ-011: Prescription refills (Pending Detail)
- RULE-020: Pharmacy benefit rules (Active)

**Generated Answer:**
```
For prescription refills, the process typically involves:
- Contacting your pharmacy
- Using mail-order services if available
- Working with your doctor for new prescriptions

For specific refill instructions for your plan and pharmacy network:
- Contact customer service at [number]
- Check your member portal
- Call your pharmacy's customer service

Our team can provide step-by-step guidance for your specific situation.
```

**Why Safe:**
- General guidance only (not specific operational steps)
- "Pending Detail" status acknowledged with strong disclaimer
- Defers operational specifics to customer service
- Avoids potential errors from incomplete operational info

**Required Disclaimers:**
- ✅ "Contact customer service for specific instructions"
- ✅ "For your specific situation..."
- ✅ Operational disclaimer (process may vary)

---

## 4. Caveat Language Library

### Caveat Type 1: Plan-Specific Confirmation
**When to use:** Plan-specific questions + placeholder or incomplete data

**Caveat Language:**
```
"Coverage details vary by plan. Check your policy documents or contact customer 
service at [number] to confirm your specific coverage."
```

---

### Caveat Type 2: Network Verification
**When to use:** Provider/hospital questions + network placeholder or no verification

**Caveat Language:**
```
"To verify provider network status for your plan, check our provider directory 
at [URL] or contact customer service at [number] before scheduling your appointment. 
Provider participation can change."
```

---

### Caveat Type 3: Cost/Pricing Confirmation
**When to use:** Cost questions + placeholder or cost-related data

**Caveat Language:**
```
"Costs vary by plan, provider, and service. For accurate cost estimates:
- Check your policy documents for copays and deductibles
- Contact customer service at [number]
- Ask your provider for a cost estimate before service"
```

---

### Caveat Type 4: Operational Process
**When to use:** "How do I..." questions + Pending Detail FAQ

**Caveat Language:**
```
"For step-by-step instructions specific to your plan and situation, contact 
customer service at [number]. Our team can guide you through the process."
```

---

### Caveat Type 5: Policy Interpretation
**When to use:** Complex policy questions + Rule-only retrieval or Needs Review

**Caveat Language:**
```
"Policy interpretation may vary depending on your specific circumstances. For 
personalized guidance, contact customer service at [number] or consult your 
policy documents."
```

---

### Caveat Type 6: Compliance/Legal
**When to use:** Compliance questions + sensitive policy matters

**Caveat Language:**
```
"This is a compliance matter. For guidance specific to your situation, please 
contact our compliance team through customer service at [number]."
```

---

## 5. Answer Generation Decision Tree

```
START: Retrieved chunks identified
  |
  ├─→ Any is_placeholder=true?
  |     ├─→ YES: Customer-facing?
  |     |     ├─→ YES: FILTER OUT placeholder, use FAQ/Rule only + disclaimer
  |     |     └─→ NO (internal): Include placeholder with warning label
  |     └─→ NO: Proceed
  |
  ├─→ Any status=Pending Detail or Needs Review?
  |     ├─→ YES: Add operational/policy disclaimer
  |     └─→ NO: Proceed
  |
  ├─→ Plan-specific question? (requires_plan_confirmation=true)
  |     ├─→ YES: Add plan confirmation caveat
  |     └─→ NO: Proceed
  |
  ├─→ Network question? (requires_network_verification=true)
  |     ├─→ YES: Add network verification caveat
  |     └─→ NO: Proceed
  |
  ├─→ Only Rule retrieved? (no FAQ match)
  |     ├─→ YES: Add policy interpretation caveat
  |     └─→ NO: Proceed
  |
  └─→ Generate answer from highest-confidence sources
        Apply weakest-link overall confidence
        Add caveats as determined above
```

---

## 6. Implementation Pseudocode

```python
def generate_safe_answer(query, retrieved_chunks):
    """Generate answer with appropriate safety behavior"""
    
    # Step 1: Analyze retrieved chunks
    has_placeholder = any(c['is_placeholder'] for c in retrieved_chunks)
    has_pending_detail = any(c['status'] == 'Pending Detail' for c in retrieved_chunks)
    has_needs_review = any(c['status'] == 'Needs Review' for c in retrieved_chunks)
    has_faq = any(c['chunk_type'] == 'FAQ' for c in retrieved_chunks)
    has_rule = any(c['chunk_type'] == 'Rules' for c in retrieved_chunks)
    
    # Step 2: Determine answer sources
    if use_case == "customer-facing":
        # Filter out placeholders for customer-facing
        answer_sources = [c for c in retrieved_chunks if not c['is_placeholder']]
    else:
        # Internal use: keep placeholders but label
        answer_sources = retrieved_chunks
    
    # Step 3: Check if we have enough non-placeholder sources
    if len(answer_sources) == 0:
        # UNSAFE: Only placeholders retrieved (should not happen if filtering correct)
        return generate_fallback_answer()
    
    # Step 4: Determine overall confidence (weakest link)
    confidence_levels = [get_confidence(c) for c in answer_sources]
    overall_confidence = min(confidence_levels)  # Weakest link
    
    # Step 5: Generate base answer
    base_answer = llm.generate(query, answer_sources)
    
    # Step 6: Determine required caveats
    caveats = []
    
    if has_placeholder:
        caveats.append("plan_specific_confirmation")
    
    if requires_plan_confirmation(query, answer_sources):
        caveats.append("plan_specific_confirmation")
    
    if requires_network_verification(query, answer_sources):
        caveats.append("network_verification")
    
    if has_pending_detail:
        caveats.append("operational_process")
    
    if has_needs_review or (has_rule and not has_faq):
        caveats.append("policy_interpretation")
    
    # Step 7: Add caveats to answer
    final_answer = base_answer
    for caveat_type in set(caveats):  # Deduplicate
        final_answer += "\n\n" + get_caveat_language(caveat_type)
    
    # Step 8: Log for monitoring
    log_answer_generation({
        "query": query,
        "sources": [c['chunk_id'] for c in answer_sources],
        "confidence": overall_confidence,
        "caveats": caveats,
        "has_placeholder": has_placeholder
    })
    
    return final_answer
```

---

## 7. Testing Scenarios

### Test 1: FAQ+Rule (No Disclaimers)
**Query:** "What is a deductible?"  
**Expected:** Confident answer, no disclaimers  
**Validate:** No caveats added  

---

### Test 2: Plan-Specific + Placeholder
**Query:** "Does my Basic Family Plan cover dental?"  
**Expected:** General guidance + plan confirmation disclaimer  
**Validate:** Placeholder not stated as fact, disclaimer present  

---

### Test 3: Network + Placeholder
**Query:** "Is Dubai Medical Center in-network?"  
**Expected:** Network verification process + verification disclaimer  
**Validate:** Network status NOT confirmed, disclaimer present  

---

### Test 4: Operational + Pending Detail
**Query:** "How do I refill a prescription?"  
**Expected:** General guidance + contact customer service disclaimer  
**Validate:** Operational disclaimer present  

---

### Test 5: Policy + Needs Review
**Query:** "What if I don't disclose pre-existing condition?"  
**Expected:** Policy guidance + policy interpretation disclaimer  
**Validate:** Compliance caution present  

---

### Test 6: Placeholder-Only (Error Scenario)
**Query:** "What plans do you offer?"  
**Expected:** Fallback answer, defer to customer service  
**Validate:** NO placeholder content used, incident logged  

---

## 8. Monitoring Metrics

### Metric 1: Caveat Distribution
**Track:** % answers with each caveat type  
**Target:** Plan-specific 20-30%, Network 5-10%, Operational 10-15%  
**Action if Off:** Review content gaps, update FAQ  

---

### Metric 2: Placeholder Appearance Rate
**Track:** % answers where placeholder was in top-10 retrieval  
**Target:** 0% for customer-facing, <20% for internal  
**Action if Off:** Investigate filtering/weighting issues  

---

### Metric 3: Overall Confidence Distribution
**Track:** % answers by confidence (High/Medium/Low)  
**Target:** High >70%, Medium 20-30%, Low <10%  
**Action if Off:** Review content quality, update FAQ/Rules  

---

### Metric 4: FAQ Coverage Rate
**Track:** % queries with at least one FAQ match  
**Target:** >80%  
**Action if Off:** Identify content gaps, create new FAQ  

---

## 9. Document Control

**Filename:** ANSWER_SAFETY_BEHAVIOR.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- PLACEHOLDER_ENFORCEMENT_SPEC.md - Placeholder operational rules
- CHUNK_FILTERING_RULES.md - Filtering by use case
- RETRIEVAL_WEIGHTING_SPEC.md - Retrieval weights
- VALIDATION_AND_QA_SPEC.md - Testing scenarios

---

**END OF ANSWER SAFETY BEHAVIOR SPECIFICATION**

**CRITICAL REMINDER:** Answer safety depends on the WEAKEST LINK in retrieved chunks, not just the strongest source.
