# Prototype Query Handling Specification

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document defines **how different types of user queries should be handled** in the internal RAG prototype, specifying the retrieval strategy, source prioritization, and response behavior for each query category.

---

## Query Type Classification

The prototype recognizes **7 main query types**:

1. **Conceptual Questions** - General insurance concepts
2. **Policy/Rules Questions** - Policy reasoning and benefit rules
3. **Plan-Specific Questions** - Questions about specific plan details
4. **Network-Specific Questions** - Provider network status inquiries
5. **Operational/Process Questions** - How to perform actions (claims, refills, etc.)
6. **Mixed Questions** - Combination of multiple types
7. **Unsupported/System Questions** - Out of scope for prototype

---

## Query Type 1: Conceptual Questions

### Definition
Questions about general insurance concepts, definitions, and terminology.

### Examples
- "What is a deductible?"
- "What does copay mean?"
- "What is the difference between in-network and out-of-network?"
- "What are pre-existing conditions?"
- "What is coinsurance?"

### Handling Strategy

**Primary Source:** FAQ chunks (Approved/Active, High confidence)

**Secondary Source:** Rules chunks (for detailed reasoning)

**Tertiary Source:** Mapping chunks (for related concepts)

**Placeholder Involvement:** NONE (not relevant to conceptual questions)

**Retrieval Flow:**
1. Retrieve top 3-5 FAQ chunks matching the concept
2. Retrieve 1-2 Rules chunks for supporting reasoning
3. Optionally retrieve Mapping for related concepts

**Expected Confidence Tier:** Tier 1 (Strongest) - FAQ + Rules only, no placeholders

**Response Behavior:**
- Direct, confident answer using FAQ wording
- Include reasoning from Rules if helpful
- Minimal or no disclaimers needed
- Provide examples if available in FAQ
- Cross-reference related concepts if Mapping suggests

**Disclaimers Required:** NONE (unless FAQ status is Pending Detail)

**Example Answer Pattern:**
```
A deductible is the amount you pay out-of-pocket for covered healthcare 
services before your insurance plan begins to pay. For example, if your 
deductible is $1,000, you pay the first $1,000 of covered services yourself.

Once you meet your deductible, your insurance starts covering a portion of 
costs, though you may still have copays or coinsurance depending on your plan.

Related concepts: copay, coinsurance, out-of-pocket maximum
```

**Success Criteria:**
- ✅ Retrieves relevant FAQ in top 3 results
- ✅ Answer uses customer-friendly language from FAQ
- ✅ No placeholder involvement
- ✅ Confidence tier = Tier 1

---

## Query Type 2: Policy/Rules Questions

### Definition
Questions about policy rules, benefit logic, and coverage reasoning.

### Examples
- "What is the copay for specialist visits?"
- "Are pre-existing conditions covered?"
- "What happens if I don't disclose a pre-existing condition?"
- "How does the approval process work for specialist referrals?"
- "What are the maternity coverage requirements?"

### Handling Strategy

**Primary Source:** Rules chunks (Active/Approved) + FAQ chunks

**Secondary Source:** Mapping chunks (cross-linkage)

**Tertiary Source:** Plans placeholders (if query mentions specific plan, for context only)

**Placeholder Involvement:** LOW (only if plan name mentioned, for recognition not truth)

**Retrieval Flow:**
1. Retrieve top 3-5 Rules chunks matching the policy question
2. Retrieve 2-3 FAQ chunks for customer-friendly context
3. Retrieve Mapping to identify related rules
4. If plan name mentioned, retrieve plan placeholder for context only

**Expected Confidence Tier:** 
- Tier 1 (Strongest) if no plan name mentioned
- Tier 2 (Strong) if Mapping involved
- Tier 3 (Moderate) if plan placeholder present

**Response Behavior:**
- Provide policy reasoning from Rules
- Use FAQ for customer-friendly explanation
- If plan-specific: provide general rule + add disclaimer about plan variation
- Cite policy logic clearly
- Be honest if rule status is "Needs Review" (add caution disclaimer)

**Disclaimers Required:**
- If `requires_plan_confirmation = TRUE`: "Coverage details vary by plan. Check your policy documents."
- If Rules status = "Needs Review": "For personalized guidance, consult your policy documents or contact compliance."
- If plan name mentioned but only placeholder available: "Check your policy documents for plan-specific details."

**Example Answer Pattern (General Policy):**
```
According to policy rules, specialist visits typically have a copay that varies 
by plan tier. Most plans require copays between $30-$75 for specialist visits.

Pre-authorization may be required for certain specialists. Check with customer 
service before scheduling to confirm if authorization is needed.

**Note:** Copay amounts vary by plan. Check your policy documents or contact 
customer service for your specific copay.
```

**Example Answer Pattern (Plan-Specific Policy):**
```
Pre-existing conditions are generally covered under most plans, but disclosure 
requirements apply. You must disclose pre-existing conditions during enrollment.

For your specific plan's pre-existing condition coverage terms, please:
- Review your policy documents (Section: Pre-Existing Conditions)
- Contact customer service at [number]
- Consult with your HR benefits coordinator

**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service.
```

**Success Criteria:**
- ✅ Retrieves relevant Rules in top 5 results
- ✅ Provides policy reasoning clearly
- ✅ Adds disclaimer when plan confirmation required
- ✅ Confidence tier ≥ Tier 3

---

## Query Type 3: Plan-Specific Questions

### Definition
Questions asking about specific plan benefits, coverage, or features.

### Examples
- "Does Basic Family Plan cover dental?"
- "What's the deductible for the Premium Individual Plan?"
- "Does the Economy Plan include maternity coverage?"
- "What's covered under the Corporate Group Plan?"
- "How much is the copay on the Starter Plan?"

### Handling Strategy

**Primary Source:** FAQ chunks (general benefit explanations)

**Secondary Source:** Rules chunks (benefit logic and categories)

**Tertiary Source:** Plans placeholders (recognize plan name, DO NOT state placeholder details as facts)

**Placeholder Involvement:** HIGH (plan name recognition) but LOW (not trusted for truth)

**Critical Rule:** Placeholder Plans are ALL placeholders awaiting real product data. DO NOT state placeholder content as confirmed plan benefits.

**Retrieval Flow:**
1. Retrieve FAQ chunks about the benefit type (e.g., dental coverage general)
2. Retrieve Rules chunks about benefit categories and logic
3. Retrieve Plans placeholder to recognize plan name (e.g., "Basic Family Plan")
4. **Downweight placeholder heavily** (score × 0.08)
5. Use FAQ + Rules for general guidance
6. Use placeholder ONLY to recognize plan name in context
7. **Mandatory disclaimer** about checking policy documents

**Expected Confidence Tier:** Tier 3 (Moderate) - FAQ + Rules + Placeholder present

**Response Behavior:**
- Provide **general guidance** about the benefit type from FAQ/Rules
- Acknowledge the plan name mentioned (recognized from placeholder)
- **DO NOT state placeholder details as confirmed facts**
- **Mandatory disclaimer:** "Check your policy documents for plan-specific details"
- Provide contact information for definitive answer
- Suggest where to find confirmation (policy docs, customer service, member portal)

**Disclaimers Required:**
- ✅ **ALWAYS: "Coverage details vary by plan. Check your policy documents or contact customer service."**
- ✅ If network-related: "Verify provider network status before scheduling appointment."
- ✅ If cost-related: "Costs vary by plan. Contact customer service for specific pricing."

**Example Answer Pattern:**
```
Dental coverage varies by plan type and tier. Many plans include preventive 
dental care (cleanings, exams), and some plans include additional coverage 
for basic and major procedures.

For specific dental coverage details for your Basic Family Plan, please:
- Check your policy documents or benefits summary
- Contact customer service at [number]
- Log into your member portal and review plan benefits

**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service.
```

**What NOT to Say (Placeholder Leakage):**
```
❌ "Yes, the Basic Family Plan covers dental with a $25 copay for preventive 
care and 50% coinsurance for major procedures."

Why wrong: This states placeholder details as confirmed fact, creating legal 
liability if placeholder data is inaccurate.
```

**Success Criteria:**
- ✅ Provides general benefit guidance from FAQ/Rules
- ✅ Recognizes plan name from placeholder
- ✅ Does NOT state placeholder details as facts
- ✅ Includes mandatory disclaimer
- ✅ Placeholder score < 0.1 (heavily downweighted)
- ✅ Confidence tier = Tier 3

---

## Query Type 4: Network-Specific Questions

### Definition
Questions about provider network status, in-network vs out-of-network, or specific providers.

### Examples
- "Is Dr. Ahmed in-network?"
- "Is Dubai Medical Center covered?"
- "Can I see out-of-network providers?"
- "What's the difference between in-network and out-of-network coverage?"
- "How do I find an in-network provider?"

### Handling Strategy

**Primary Source:** FAQ chunks (network verification process, general network rules)

**Secondary Source:** Rules chunks (network policies, billing differences)

**Tertiary Source:** Network placeholders (recognize provider name, DO NOT confirm network status)

**Placeholder Involvement:** HIGH (provider name recognition) but LOW (not trusted for truth)

**Critical Rule:** Placeholder Network chunks are ALL placeholders awaiting real provider contracts. DO NOT confirm provider network status from placeholder content.

**Retrieval Flow:**
1. Retrieve FAQ chunks about network verification process
2. Retrieve FAQ chunks about in-network vs out-of-network differences
3. Retrieve Rules chunks about network policies and billing
4. Retrieve Network placeholder to recognize provider/facility name
5. **Downweight placeholder heavily** (score × 0.08)
6. Use FAQ + Rules for general network guidance
7. Use placeholder ONLY to recognize provider name
8. **Mandatory disclaimer** about verifying before appointment

**Expected Confidence Tier:** Tier 3 (Moderate) - FAQ + Rules + Placeholder present

**Response Behavior:**
- Provide **network verification process** from FAQ
- Explain **general network rules** from Rules (in-network vs out-of-network)
- Acknowledge the provider name mentioned (recognized from placeholder)
- **DO NOT confirm network status from placeholder**
- **Mandatory disclaimer:** "Verify provider network status before scheduling appointment"
- Provide specific steps to verify (customer service, online directory, member portal)

**Disclaimers Required:**
- ✅ **ALWAYS: "Provider network status may vary. Verify with customer service before scheduling appointment."**
- ✅ "Network status can change. Always confirm before receiving services."
- ✅ "For current network status, contact customer service at [number]."

**Example Answer Pattern:**
```
To verify if a provider is in your network, you can:
1. Call customer service at [number] with the provider's name and location
2. Log into your member portal and use the provider directory search
3. Ask the provider's office to verify your insurance coverage before your appointment

In-network providers have contracted rates with the insurance company, resulting 
in lower out-of-pocket costs. Out-of-network providers may charge higher rates 
and may require you to pay upfront and file for reimbursement.

**Important:** Provider network status can change. Always verify before scheduling 
your appointment to avoid unexpected costs.
```

**What NOT to Say (Placeholder Leakage):**
```
❌ "Yes, Dr. Ahmed is in-network. You can see Dr. Ahmed at Dubai Medical Center."

Why wrong: This confirms network status from placeholder data, which is not 
verified. Patient might incur out-of-network costs if placeholder is inaccurate.
```

**Success Criteria:**
- ✅ Provides network verification process from FAQ
- ✅ Explains network rules from Rules
- ✅ Recognizes provider name from placeholder
- ✅ Does NOT confirm network status as fact
- ✅ Includes mandatory verification disclaimer
- ✅ Placeholder score < 0.1
- ✅ Confidence tier = Tier 3

---

## Query Type 5: Operational/Process Questions

### Definition
Questions about how to perform actions, processes, or procedures (claims, refills, logins, etc.).

### Examples
- "How do I file a claim?"
- "How do I refill a prescription?"
- "How do I log into my account?"
- "How do I add a dependent?"
- "How do I contact customer service?"

### Handling Strategy

**Primary Source:** FAQ chunks (process explanations)

**Secondary Source:** Rules chunks (process policies)

**Tertiary Source:** NONE (placeholders not relevant)

**Placeholder Involvement:** NONE

**Retrieval Flow:**
1. Retrieve FAQ chunks about the specific process
2. Retrieve Rules chunks about process policies if available
3. No placeholder retrieval needed

**Expected Confidence Tier:** 
- Tier 1 (Strongest) if FAQ status = Approved
- Tier 2 (Strong) if FAQ status = Pending Detail (incomplete process details)

**Response Behavior:**
- Provide **general process guidance** from FAQ
- If FAQ status = "Pending Detail": provide high-level steps + strong disclaimer
- Always recommend contacting customer service for step-by-step personalized guidance
- Provide contact information prominently
- Be honest if process details are incomplete in KB

**Disclaimers Required:**
- If FAQ status = "Pending Detail": **"Contact customer service at [number] for step-by-step instructions specific to your situation."**
- If process varies by plan/situation: "Process may vary. Contact customer service for personalized guidance."

**Example Answer Pattern (Approved FAQ):**
```
To file a claim for reimbursement:
1. Obtain an itemized bill from your healthcare provider
2. Complete the claim form (available on member portal or customer service)
3. Submit the claim form and itemized bill via:
   - Member portal (fastest)
   - Email to claims@insurance.com
   - Mail to [address]
4. Claims are typically processed within 15-30 business days

For questions about your specific claim, contact customer service at [number].
```

**Example Answer Pattern (Pending Detail FAQ):**
```
To refill a prescription, you can typically:
- Use your pharmacy's online refill system
- Call your pharmacy directly
- Visit the pharmacy in person

For detailed instructions specific to your insurance plan and pharmacy network, 
please contact customer service at [number].

**Note:** Contact customer service at [number] for step-by-step instructions 
specific to your situation.
```

**Success Criteria:**
- ✅ Retrieves relevant process FAQ
- ✅ Provides clear process steps if available
- ✅ Adds disclaimer if details incomplete
- ✅ Always provides contact information
- ✅ No placeholder involvement

---

## Query Type 6: Mixed Questions

### Definition
Questions that combine multiple query types (e.g., plan-specific + network-specific).

### Examples
- "Does my Basic Family Plan cover Dr. Ahmed for maternity services?"
- "What's the copay on the Premium Plan for in-network specialists?"
- "How do I file a claim for out-of-network emergency care on my Corporate Plan?"

### Handling Strategy

**Decompose into Sub-Queries:**
1. Identify all query components
2. Handle each component according to its query type
3. Combine answers with appropriate disclaimers

**Example Decomposition:**
Query: "Does my Basic Family Plan cover Dr. Ahmed for maternity services?"
- Component 1: Plan-specific (Basic Family Plan + maternity) → Query Type 3
- Component 2: Network-specific (Dr. Ahmed) → Query Type 4
- Component 3: Benefit type (maternity services) → Query Type 1/2

**Retrieval Flow:**
1. Retrieve FAQ about maternity coverage (general)
2. Retrieve Rules about maternity policies
3. Retrieve FAQ about network verification
4. Retrieve Plans placeholder (recognize "Basic Family Plan")
5. Retrieve Network placeholder (recognize "Dr. Ahmed")
6. Downweight both placeholders heavily

**Expected Confidence Tier:** Tier 3 (Moderate) - Multiple placeholders present

**Response Behavior:**
- Address each component separately
- Provide general guidance for each aspect
- **DO NOT state any placeholder details as facts**
- **Multiple disclaimers required** (plan confirmation + network verification)
- Provide clear next steps for verification

**Disclaimers Required:**
- ✅ Plan confirmation: "Check your policy documents for plan-specific maternity coverage."
- ✅ Network verification: "Verify Dr. Ahmed's network status and maternity coverage before scheduling."
- ✅ Combined: "Contact customer service to confirm both plan coverage and provider network status."

**Example Answer Pattern:**
```
Maternity coverage varies by plan type and includes prenatal care, delivery, 
and postnatal care. Most plans cover maternity services, but coverage details 
(copays, deductibles, hospital stay limits) vary by plan tier.

For your Basic Family Plan's specific maternity coverage:
- Check your policy documents (Section: Maternity Benefits)
- Contact customer service at [number]

To verify if Dr. Ahmed provides maternity services in your network:
- Call customer service with Dr. Ahmed's name and location
- Use the member portal provider directory
- Ask Dr. Ahmed's office to verify your insurance coverage

**Important:** 
- Coverage details vary by plan. Check your policy documents or contact customer service.
- Provider network status may vary. Verify before scheduling appointment.
```

**Success Criteria:**
- ✅ Addresses all query components
- ✅ Provides general guidance for each aspect
- ✅ Does NOT state placeholder details as facts
- ✅ Includes all required disclaimers
- ✅ Provides clear verification steps
- ✅ Confidence tier = Tier 3

---

## Query Type 7: Unsupported/System Questions

### Definition
Questions that are out of scope for the KB or prototype, such as account-specific data, system status, or topics not covered.

### Examples
- "What's my current claim status?"
- "How much have I paid toward my deductible this year?"
- "Is the claims portal down?"
- "What's my member ID?"
- "Can I change my plan now?"
- "What's the weather?" (completely off-topic)

### Handling Strategy

**Detection:**
- Query asks for personal account data (not in KB)
- Query asks for real-time system status (not in KB)
- Query asks for topics with no relevant FAQ/Rules/Mapping (semantic match < 0.5)
- Query is off-topic (insurance-unrelated)

**Retrieval Flow:**
1. Attempt retrieval as normal
2. If no sources score > 0.5 → unsupported query detected
3. If query is account-specific → detected via keywords ("my claim", "my deductible", "my ID")

**Expected Confidence Tier:** Tier 5 (Unsafe) - No reliable sources or account-specific

**Response Behavior:**
- **DO NOT attempt to answer from weak sources**
- Provide safe fallback response
- Direct to customer service
- Be honest that prototype cannot answer this query type

**Disclaimers Required:**
- ✅ "I don't have information on that topic."
- ✅ "For account-specific information, please log into your member portal or contact customer service."
- ✅ "This topic is outside my current knowledge. Contact customer service at [number] for assistance."

**Example Answer Pattern (Unsupported Topic):**
```
I don't have reliable information on that specific topic. For accurate information, 
please contact customer service at [number] or visit our website at [url].
```

**Example Answer Pattern (Account-Specific):**
```
For account-specific information like claim status, deductible balance, or member 
ID, please:
- Log into your member portal at [url]
- Contact customer service at [number]
- Review your most recent Explanation of Benefits (EOB)

Customer service representatives have access to your account details and can 
provide personalized assistance.
```

**Example Answer Pattern (System Status):**
```
For current system status and technical support:
- Check the system status page at [url]
- Contact technical support at [number]
- Try logging out and logging back in
- Clear your browser cache and cookies

If the issue persists, contact technical support for further assistance.
```

**Success Criteria:**
- ✅ Detects unsupported queries (semantic match < 0.5)
- ✅ Detects account-specific queries (keyword matching)
- ✅ Provides safe fallback response
- ✅ Does NOT attempt weak answer from low-confidence sources
- ✅ Directs to appropriate contact channel
- ✅ Confidence tier = Tier 5

---

## Query Handling Decision Matrix

| Query Type | Primary Source | Secondary Source | Placeholder Use | Conf. Tier | Disclaimers | Caution Level |
|------------|----------------|------------------|-----------------|------------|-------------|---------------|
| **Conceptual** | FAQ | Rules, Mapping | NONE | Tier 1 | Minimal | Low |
| **Policy/Rules** | Rules, FAQ | Mapping | Low (recognition) | Tier 1-3 | Moderate | Medium |
| **Plan-Specific** | FAQ, Rules | Plans placeholder | HIGH (recognition only) | Tier 3 | **ALWAYS** | **HIGH** |
| **Network-Specific** | FAQ, Rules | Network placeholder | HIGH (recognition only) | Tier 3 | **ALWAYS** | **HIGH** |
| **Operational/Process** | FAQ | Rules | NONE | Tier 1-2 | Moderate | Medium |
| **Mixed** | All relevant | Multiple placeholders | HIGH (recognition only) | Tier 3 | **MULTIPLE** | **HIGH** |
| **Unsupported** | NONE | NONE | NONE | Tier 5 | Fallback | **CRITICAL** |

---

## Query Intent Classification (Prototype Approach)

For the internal prototype, simple keyword-based classification is sufficient:

### Conceptual Keywords
- "what is", "what does", "what are", "define", "explain", "meaning of"
- "difference between", "vs", "versus"
- Combined with: "deductible", "copay", "coinsurance", "premium", "network", "pre-existing", etc.

### Policy/Rules Keywords
- "policy", "rule", "coverage", "covered", "benefit", "requirement"
- "approval", "authorization", "referral", "disclosure"
- "copay for", "deductible for", "how much", "what happens if"

### Plan-Specific Keywords
- Specific plan names: "Basic Family Plan", "Premium Individual", "Economy Plan", "Corporate Group"
- "my plan", "our plan", "this plan"
- Combined with benefit questions

### Network-Specific Keywords
- Provider names: "Dr.", "Medical Center", "Hospital", "Clinic", "Pharmacy"
- "in-network", "out-of-network", "network status", "covered provider"
- "can I see", "is [provider] covered"

### Operational/Process Keywords
- "how do I", "how to", "how can I", "steps to"
- "file a claim", "refill prescription", "log in", "add dependent", "contact", "reset password"

### Account-Specific Keywords
- "my claim", "my deductible", "my balance", "my ID", "my account"
- "current status", "have I paid", "how much have I"

### Off-Topic Detection
- If semantic match to all FAQ/Rules/Mapping < 0.5 → likely off-topic

---

## Monitoring Query Handling Quality

During internal testing, track:

1. **Query Type Distribution:**
   - What % of queries are conceptual? (expect 30-40%)
   - What % are plan-specific? (expect 20-30%)
   - What % are unsupported? (expect <10%)

2. **Confidence Tier Distribution:**
   - What % achieve Tier 1 (strongest)? (target >50%)
   - What % fall to Tier 3 (moderate)? (expect 20-30%)
   - What % fall to Tier 5 (unsafe fallback)? (target <10%)

3. **Disclaimer Firing:**
   - Are disclaimers added for all plan-specific queries? (target 100%)
   - Are disclaimers added for all network-specific queries? (target 100%)
   - Are disclaimers NOT added for conceptual queries? (target 100%)

4. **Placeholder Behavior:**
   - Are placeholders score < 0.1? (target 100%)
   - Are placeholder details NEVER stated as facts? (target 100% compliance)

5. **Answer Quality:**
   - Are answers using appropriate FAQ wording?
   - Are answers providing sufficient context?
   - Are answers honest about limitations?

---

## Implementation Notes for Engineering

### Query Classification Implementation

**Approach 1: Rule-Based (Recommended for Prototype)**
```python
def classify_query(query):
    query_lower = query.lower()
    
    # Account-specific (highest priority, immediate detection)
    if any(keyword in query_lower for keyword in ["my claim", "my deductible", "my id", "my balance"]):
        return "account-specific"
    
    # Plan-specific
    if any(plan_name in query_lower for plan_name in ["basic family", "premium individual", "economy plan"]):
        return "plan-specific"
    
    # Network-specific
    if any(keyword in query_lower for keyword in ["dr.", "medical center", "hospital", "in-network"]):
        return "network-specific"
    
    # Operational/Process
    if query_lower.startswith("how do i") or query_lower.startswith("how to"):
        return "operational"
    
    # Conceptual
    if query_lower.startswith("what is") or query_lower.startswith("what does"):
        return "conceptual"
    
    # Policy/Rules
    if any(keyword in query_lower for keyword in ["policy", "rule", "coverage", "benefit"]):
        return "policy"
    
    # Default: attempt retrieval, fallback to unsupported if low confidence
    return "unknown"
```

**Approach 2: ML-Based (Future Enhancement)**
- Train a simple classifier on labeled query dataset
- Use transformer-based models for intent classification
- Can be added in Phase 2

### Query Handling Implementation

Once query type is classified, route to appropriate handler:

```python
def handle_query(query, query_type):
    if query_type == "conceptual":
        return handle_conceptual_query(query)
    elif query_type == "plan-specific":
        return handle_plan_specific_query(query)
    elif query_type == "network-specific":
        return handle_network_specific_query(query)
    # ... etc.
    else:
        return handle_unsupported_query(query)
```

Each handler implements the retrieval flow and response behavior defined in this document.

---

## Document Control

**Filename:** PROTOTYPE_QUERY_HANDLING.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_SCOPE.md - What is in/out of scope
- PROTOTYPE_RETRIEVAL_FLOW.md - Step-by-step retrieval process
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Answer generation rules (next)
- PROTOTYPE_TEST_QUERIES.md - Test query set (next)
- HANDOFF_TO_ENGINEERING.md - Implementation handoff

---

**END OF QUERY HANDLING SPECIFICATION**
