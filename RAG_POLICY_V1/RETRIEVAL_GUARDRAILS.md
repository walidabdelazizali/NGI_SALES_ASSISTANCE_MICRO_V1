# Retrieval Guardrails - Micro Insurance KB V1

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define safety rules for RAG retrieval and answer generation  
**Enforcement Level:** MANDATORY for production deployment

---

## 1. Purpose and Scope

This document defines **NON-NEGOTIABLE** safety rules that MUST be enforced in any RAG retrieval system using the Micro Insurance KB V1 package. These guardrails prevent:

- ❌ Presenting placeholder data as confirmed insurance facts
- ❌ Overstating plan benefits when data is incomplete
- ❌ Claiming provider availability without verification
- ❌ Legal liability from misinformation
- ❌ Regulatory violations from unverified claims

**Golden Rule:** **When in doubt, add a disclaimer and defer to verified sources.**

---

## 2. Fundamental Guardrail Principles

### Principle 1: Truth Hierarchy

Not all knowledge chunks have equal truth value:

```
Tier 1 (Strong Truth):
├── FAQ chunks (status = Approved) ────────► High confidence
├── Rules chunks (status = Active) ────────► High confidence
└── Mapping chunks (confidence = High) ────► Medium confidence

Tier 2 (Weak Truth):
├── FAQ chunks (status = Needs Review) ────► Medium confidence
├── FAQ chunks (status = Pending Detail) ──► Low confidence
└── Mapping chunks (confidence = Low) ─────► Low confidence

Tier 3 (Placeholder Only - NOT Truth):
├── Plans chunks (ALL) ────────────────────► Structural placeholder
└── Network chunks (ALL) ──────────────────► Structural placeholder
```

**Guardrail:** Retrieval MUST prioritize Tier 1 content. Tier 3 content MUST NEVER be presented as confirmed truth.

---

### Principle 2: Placeholder Isolation

Placeholder content (plans, network) exists for structure and routing only, NOT for final customer answers.

**Guardrail:** Any answer derived from `is_placeholder: true` chunks MUST:
1. Include explicit verification disclaimer
2. Direct user to authoritative sources (policy documents, customer service)
3. Never state placeholder data as fact

---

### Principle 3: Confidence-Based Caution

Lower confidence content requires extra caution.

**Guardrail:** 
- High confidence (>0.9): Can answer directly
- Medium confidence (0.5-0.9): Can answer with light disclaimer
- Low confidence (<0.5): Must add strong disclaimer or defer to verified sources

---

### Principle 4: Dependency Awareness

Some questions depend on plan-specific or network-specific truth.

**Guardrail:** When `requires_plan_confirmation: true` or `requires_network_verification: true`, answer MUST acknowledge dependency and require verification.

---

## 3. Mandatory Filtering Rules

### Rule 3.1: Customer-Facing Retrieval Filter

**For direct customer answers (chatbot, FAQ page, self-service):**

```
MUST INCLUDE: is_placeholder = false AND safe_for_client_direct_use = true
MUST EXCLUDE: is_placeholder = true OR safe_for_client_direct_use = false

OR

IF is_placeholder = true, THEN answer MUST include verification disclaimer
```

**Rationale:** Customers should receive only approved, non-placeholder content unless explicitly warned.

---

### Rule 3.2: Status-Based Filtering

**For production answers:**

```
RECOMMENDED: status IN ('Approved', 'Active')
CAUTION: status = 'Needs Review' (add disclaimer)
AVOID: status = 'Pending Detail' (defer to customer service)
NEVER: status = 'Deprecated' (exclude completely)
```

**Rationale:** Only approved content provides reliable answers.

---

### Rule 3.3: Retrieval Weight Enforcement

**Apply weight hints to retrieval scoring:**

```
FAQ + Rules (Approved/Active): weight = 1.0 (full strength)
Mapping (High confidence): weight = 0.6
Mapping (Medium confidence): weight = 0.5
Mapping (Low confidence): weight = 0.4
Plans (Placeholder): weight = 0.2 (minimal)
Network (Placeholder): weight = 0.2 (minimal)
```

**Rationale:** Ensures strong knowledge dominates retrieval results.

---

## 4. Answer Generation Guardrails

### Guardrail 4.1: Plan-Specific Questions

**Trigger Condition:** Question asks about specific plan benefits, coverage limits, copays, or plan details.

**Required Behavior:**
```
IF question requires plan-specific truth:
    IF is_placeholder = true OR requires_plan_confirmation = true:
        THEN answer MUST include:
        "Specific plan details vary based on your coverage. 
         Please check your policy documents or contact customer service 
         for accurate information about your plan benefits."
```

**Examples:**

✅ **SAFE Answer:**
```
Question: "Does my plan cover dental?"
Answer: "Coverage for dental services varies by plan type. 
         Some plans include preventive dental care, while others may require 
         additional dental insurance. Please check your policy documents 
         to confirm what dental services are covered under your specific plan."
```

❌ **UNSAFE Answer:**
```
Question: "Does my plan cover dental?"
Answer: "The Basic Individual Plan covers annual dental checkups and cleanings."
(This is from PLAN-003 placeholder - NOT confirmed product!)
```

---

### Guardrail 4.2: Network/Provider Questions

**Trigger Condition:** Question asks about specific providers, network status, or provider availability.

**Required Behavior:**
```
IF question requires network-specific truth:
    IF is_placeholder = true OR requires_network_verification = true:
        THEN answer MUST include:
        "Provider network status can change. Please verify that 
         [provider name] is currently in-network by checking our online 
         provider directory or contacting customer service."
```

**Examples:**

✅ **SAFE Answer:**
```
Question: "Can I visit Dubai Medical Center?"
Answer: "Provider availability depends on the network associated with 
         your plan. To confirm whether Dubai Medical Center is in your 
         network, please check our online provider directory or contact 
         customer service for the most current information."
```

❌ **UNSAFE Answer:**
```
Question: "Can I visit Dubai Medical Center?"
Answer: "Yes, Dubai Medical Center is part of our Premium Network."
(This is from PROV-001 placeholder - NOT verified provider data!)
```

---

### Guardrail 4.3: Cost/Payment Questions

**Trigger Condition:** Question asks about deductibles, copays, out-of-pocket maximums, premiums.

**Required Behavior:**
```
IF question asks about specific costs:
    THEN answer MUST include:
        "Cost details vary based on your specific plan. Please refer to 
         your policy documents or contact customer service for accurate 
         cost information for your coverage."
```

**Examples:**

✅ **SAFE Answer:**
```
Question: "What is my deductible?"
Answer: "A deductible is the amount you pay out-of-pocket before your 
         insurance begins to pay. The specific deductible amount varies 
         by plan. Please check your policy documents or member portal 
         to see your deductible amount."
```

❌ **UNSAFE Answer:**
```
Question: "What is my deductible?"
Answer: "Your deductible is AED 1,000 per year."
(Unless retrieved from verified user-specific data!)
```

---

### Guardrail 4.4: Operational/Process Questions

**Trigger Condition:** Question asks about specific processes (card delivery, refills, login support).

**Required Behavior:**
```
IF FAQ status = 'Pending Detail' AND question is operational:
    THEN answer MUST acknowledge detail limitation:
        "For specific instructions on [process], please contact 
         customer service at [contact info] for step-by-step guidance."
```

**Affected FAQs:**
- FAQ-011: How do I refill prescriptions?
- FAQ-013: How do I access my insurance card?
- FAQ-017: How do I contact support?
- FAQ-020: Can I change my doctor or hospital?

**Examples:**

✅ **SAFE Answer:**
```
Question: "How do I refill prescriptions?"
Answer: "To refill prescriptions, you'll typically need to contact your 
         pharmacy or use their online refill system if available. For 
         specific instructions on refill procedures covered by your plan, 
         please contact customer service for detailed guidance."
```

---

### Guardrail 4.5: Low-Confidence Mapping

**Trigger Condition:** Retrieved mapping has `confidence: "Low"`.

**Required Behavior:**
```
IF mapping confidence = 'Low':
    THEN answer MAY use linked rule for reasoning, BUT MUST add:
        "This guidance is general. For questions specific to your 
         situation, please contact customer service."
```

**Affected Mappings:**
- MAP-012: I can't login to my member account
- MAP-013: How do I access my insurance card?
- MAP-017: How do I contact support?

---

## 5. Chunk Type-Specific Guardrails

### FAQ Chunks

**Usage:**
- ✅ Primary retrieval for customer questions
- ✅ Can be presented directly if status = "Approved"
- ⚠️ Add light disclaimer if status = "Needs Review"
- ⚠️ Defer to customer service if status = "Pending Detail"

**Guardrail:**
```python
if faq.status == "Approved":
    return faq.client_answer  # Safe to use directly
elif faq.status == "Needs Review":
    return faq.client_answer + "\n(Please verify with customer service if critical to your coverage.)"
elif faq.status == "Pending Detail":
    return "For detailed information on this topic, please contact customer service."
```

---

### Rules Chunks

**Usage:**
- ✅ Support FAQ answers with detailed reasoning
- ✅ Explain policy logic and business rules
- ✅ Can be referenced directly if status = "Active"
- ⚠️ Cross-check if status = "Needs Review"

**Guardrail:**
```python
if rule.status == "Active":
    use rule.client_safe_summary  # Safe for customers
    use rule.internal_usage_note  # For internal reasoning only
elif rule.status == "Needs Review":
    use with caution, add disclaimer
```

---

### Mapping Chunks

**Usage:**
- ✅ Link FAQs to related rules and context
- ✅ Enrich answers with cross-references
- ❌ NOT for direct customer display (reference only)

**Guardrail:**
```python
# Mapping chunks are for system use, not customer display
# Use to retrieve related rules, but don't show mapping text to customer

if mapping.confidence == "High":
    retrieve linked rules confidently
elif mapping.confidence == "Medium":
    retrieve linked rules with caution
elif mapping.confidence == "Low":
    retrieve linked rules but add disclaimer
```

---

### Plans Chunks (PLACEHOLDER)

**Usage:**
- ⚠️ Structural awareness only
- ⚠️ Routing and interpretation support
- ❌ NEVER present as confirmed plan benefits
- ❌ NEVER state placeholder data as fact

**Guardrail:**
```python
if chunk.is_placeholder == True and chunk.chunk_type == "Plans":
    # Can use for routing: "This sounds like a plan-specific question"
    # Can use to identify plan type context
    # CANNOT use to answer: "Your plan covers X"
    
    answer += "Specific plan details vary. Please check your policy documents."
```

**Mandatory Disclaimer:**
```
"Plan benefits and coverage details depend on your specific policy. 
 The information provided here is general guidance only. Please refer 
 to your policy documents for your exact plan benefits, exclusions, 
 and limitations."
```

---

### Network Chunks (PLACEHOLDER)

**Usage:**
- ⚠️ Structural awareness only
- ⚠️ Provider type routing support
- ❌ NEVER present as live provider directory
- ❌ NEVER confirm provider network status

**Guardrail:**
```python
if chunk.is_placeholder == True and chunk.chunk_type == "Network":
    # Can use for routing: "This sounds like a provider network question"
    # Can use to identify provider types
    # CANNOT use to answer: "Provider X is in-network"
    
    answer += "Verify provider network status with customer service."
```

**Mandatory Disclaimer:**
```
"Provider network status can change. Please verify current network 
 participation by checking our online provider directory or contacting 
 customer service before scheduling appointments."
```

---

## 6. Multi-Hop Retrieval Guardrails

When retrieval involves multiple chunks (FAQ → Mapping → Rule → Plan):

**Guardrail 6.1: Weakest Link Rule**

```
Overall confidence = MIN(confidence of all chunks in chain)

If ANY chunk in chain is placeholder:
    THEN answer MUST include placeholder disclaimer
    
If ANY chunk has confidence = "Low":
    THEN answer MUST include general disclaimer
```

**Example:**

```
Retrieved Chain:
1. FAQ-005 (status: Approved, confidence: High)
2. MAP-005 (confidence: High)
3. RULE-003 (status: Active, confidence: High)
4. PLAN-003 (is_placeholder: true, confidence: Very Low)

Result: Overall confidence = Very Low (due to placeholder)
Action: Use FAQ + Rule for general guidance, add plan verification disclaimer
```

---

## 7. Disclaimer Templates

### Standard Plan Disclaimer
```
"Specific plan details vary based on your coverage. Please check your 
 policy documents or contact customer service for accurate information 
 about your plan benefits."
```

### Standard Network Disclaimer
```
"Provider network status can change. Please verify that [provider name] 
 is currently in-network by checking our online provider directory or 
 contacting customer service."
```

### Combined Plan + Network Disclaimer
```
"Coverage and provider availability depend on your specific plan and 
 network. Please verify these details by checking your policy documents 
 and our online provider directory, or contact customer service."
```

### Pending Detail Disclaimer
```
"For specific instructions on this process, please contact customer 
 service for step-by-step guidance tailored to your situation."
```

### Low Confidence Disclaimer
```
"This guidance is general. For questions specific to your situation, 
 please contact customer service for personalized assistance."
```

### Placeholder Warning (Internal Use)
```
"[PLACEHOLDER CONTENT - NOT FOR CUSTOMER USE] This information is 
 structural only and has not been verified. Do not present as fact."
```

---

## 8. Unsafe Behavior Examples (NEVER DO)

### ❌ Anti-Pattern 1: Stating Placeholder Data as Fact

**Bad:**
```
Question: "What does the Basic Individual Plan cover?"
Answer: "The Basic Individual Plan covers outpatient visits, annual health 
         screening, emergency care, and more with a deductible of AED 500."
```

**Why Wrong:** PLAN-003 is a placeholder with unverified benefit details.

**Correct:**
```
Question: "What does the Basic Individual Plan cover?"
Answer: "Plan coverage varies by the specific policy you've selected. 
         To see full details of your plan benefits, deductibles, and 
         coverage, please check your policy documents or contact customer service."
```

---

### ❌ Anti-Pattern 2: Confirming Placeholder Provider

**Bad:**
```
Question: "Can I go to Dubai Medical Center?"
Answer: "Yes, Dubai Medical Center is part of our Premium Network."
```

**Why Wrong:** PROV-001 is a placeholder, not verified provider data.

**Correct:**
```
Question: "Can I go to Dubai Medical Center?"
Answer: "To confirm whether Dubai Medical Center is in your plan's network, 
         please check our online provider directory or contact customer service."
```

---

### ❌ Anti-Pattern 3: Ignoring Status = "Pending Detail"

**Bad:**
```
Question: "How do I refill prescriptions?"
Answer: "You can refill prescriptions at any in-network pharmacy."
```

**Why Wrong:** FAQ-011 status is "Pending Detail" - lacks operational specifics.

**Correct:**
```
Question: "How do I refill prescriptions?"
Answer: "To refill prescriptions, you'll typically contact your pharmacy 
         or use their refill system. For specific instructions on the 
         refill process covered by your plan, please contact customer 
         service for detailed guidance."
```

---

### ❌ Anti-Pattern 4: Over-Confidence from Low-Confidence Mapping

**Bad:**
```
Question: "I can't login to my member account."
Answer: "Your account is governed by our Terms of Service. You agreed 
         to these terms when you enrolled."
```

**Why Wrong:** MAP-012 has low confidence linking to RULE-016 (Terms acceptance), which is tangentially related.

**Correct:**
```
Question: "I can't login to my member account."
Answer: "For help with login issues, please contact our technical support 
         team or try the 'Forgot Password' option. They can assist with 
         account access issues."
```

---

## 9. Safe Behavior Examples (DO THIS)

### ✅ Safe Pattern 1: General Guidance + Verification

```
Question: "Does my plan cover vision care?"
Answer: "Many health insurance plans include basic vision care such as 
         eye exams, while comprehensive vision benefits may vary by plan. 
         To confirm your specific vision coverage, please check your policy 
         documents or contact customer service."
```

**Why Safe:** Provides general information without claiming placeholder plan details are real.

---

### ✅ Safe Pattern 2: Rule-Based Reasoning + Disclaimer

```
Question: "Can I add my spouse to my plan?"
Answer: "Typically, you can add eligible dependents like a spouse during 
         open enrollment or within a special enrollment period following a 
         qualifying life event. The specific process and eligibility may 
         vary, so please contact customer service to add a dependent to 
         your coverage."
```

**Why Safe:** Uses general rule logic (RULE-006) but acknowledges process may vary.

---

### ✅ Safe Pattern 3: FAQ + Context Enrichment

```
Question: "What is a pre-existing condition?"
Answer: "A pre-existing condition is a health issue you had before your 
         insurance coverage started. Depending on your policy, there may 
         be a waiting period before pre-existing conditions are covered. 
         Please check your policy documents to understand how pre-existing 
         conditions are handled under your specific plan."
```

**Why Safe:** Uses FAQ-003 (Approved status) + RULE-005 reasoning, adds plan-specific disclaimer.

---

### ✅ Safe Pattern 4: Deferring to Authoritative Source

```
Question: "What's my member ID number?"
Answer: "Your member ID number is listed on your insurance card and in 
         your online member portal. If you need help locating your member 
         ID, please contact customer service."
```

**Why Safe:** Doesn't invent data, directs to authoritative sources.

---

## 10. Testing and Validation

### Pre-Deployment Testing

Test these scenarios before production deployment:

1. **Placeholder Leak Test:**
   - Query: "What does the Basic Individual Plan cover?"
   - Expected: NO placeholder plan details in answer
   - Expected: Disclaimer about checking policy documents

2. **Network Verification Test:**
   - Query: "Is [specific hospital] in-network?"
   - Expected: NO placeholder provider data presented as fact
   - Expected: Disclaimer about verifying with provider directory

3. **Status Filtering Test:**
   - Query FAQ with status = "Pending Detail"
   - Expected: Generic guidance + defer to customer service

4. **Confidence Handling Test:**
   - Query mapped to low-confidence mapping
   - Expected: General guidance + disclaimer

5. **Multi-Hop Safety Test:**
   - Query that retrieves FAQ → Mapping → Rule → Placeholder Plan
   - Expected: Use FAQ + Rule, ignore or disclaim placeholder

---

### Ongoing Monitoring

Monitor for guardrail violations:

- **Placeholder Leak Detection:** Alert if answers contain text from placeholder chunks without disclaimers
- **Confidence Tracking:** Track when low-confidence content is retrieved
- **Disclaimer Compliance:** Verify required disclaimers are included
- **User Feedback:** Monitor complaints about incorrect information

---

## 11. Enforcement Checklist

Before production deployment, verify:

- [ ] **Placeholder filtering active:** `is_placeholder = true` chunks filtered or disclaimed
- [ ] **Weight enforcement active:** Retrieval weights applied per METADATA_SCHEMA
- [ ] **Status filtering active:** Can filter by Approved/Active for production
- [ ] **Disclaimer injection working:** Plan/network questions trigger disclaimers
- [ ] **Confidence handling working:** Low-confidence content requires disclaimers
- [ ] **Multi-hop safety working:** Weakest link rule applied to retrieval chains
- [ ] **Testing complete:** All pre-deployment tests pass
- [ ] **Monitoring configured:** Placeholder leak detection active

---

## 12. Escalation and Incident Response

**If placeholder content leaks to customer answers:**

1. **Immediate:** Filter affected chunks from retrieval
2. **Urgent:** Review logs to identify which queries triggered leak
3. **Investigate:** Determine root cause (missing filter, bug, etc.)
4. **Fix:** Update guardrails to prevent recurrence
5. **Report:** Notify Risk & Compliance team
6. **Document:** Update this policy if needed

---

## 13. Summary: Critical Guardrails

**Must enforce for production:**

1. ✅ **Filter placeholder chunks** from customer-facing retrieval OR add explicit disclaimers
2. ✅ **Apply retrieval weights** per METADATA_SCHEMA (FAQ/Rules high, placeholders very low)
3. ✅ **Inject disclaimers** for plan-specific and network-specific questions
4. ✅ **Respect status flags** (prefer Approved/Active, caution on Pending Detail)
5. ✅ **Honor confidence levels** (add disclaimers for low confidence)
6. ✅ **Validate multi-hop retrieval** (weakest link determines overall confidence)
7. ✅ **Test before deployment** (all test scenarios must pass)
8. ✅ **Monitor for violations** (detect placeholder leaks, track confidence issues)

**Golden Rule (Repeat):**

🚨 **Never present placeholder plan or network data as confirmed insurance facts.** 🚨

---

**End of Retrieval Guardrails**

✅ **Enforcement Level:** MANDATORY  
⚠️ **Violation Risk:** Legal liability, regulatory issues, customer misinformation
