# Prototype Exclusions Specification

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document explicitly defines **what the internal RAG prototype must NOT do**, establishing clear boundaries to prevent the prototype from creating false insurance certainty, making unauthorized claims, or operating outside its intended scope.

These exclusions are **mandatory safety rules** that protect both customers and the organization from liability and misinformation.

---

## Critical Exclusion Categories

The prototype has **9 critical exclusion categories**:

1. **Plan Benefit Claims** - Must not state placeholder plan details as confirmed facts
2. **Network Status Confirmation** - Must not confirm provider network status from placeholders
3. **Cost and Pricing Claims** - Must not state placeholder costs as facts
4. **Claims Adjudication** - Must not make claim approval/denial decisions
5. **Underwriting Decisions** - Must not make coverage eligibility decisions
6. **Legal/Compliance Advice** - Must not provide binding legal or compliance guidance
7. **Medical Advice** - Must not provide medical diagnosis or treatment recommendations
8. **Account Operations** - Must not perform account transactions or modifications
9. **Policy Document Replacement** - Must not claim to replace official policy documents

---

## Exclusion 1: Plan Benefit Claims

### What is Prohibited

The prototype **must NOT**:

❌ **State placeholder plan benefits as confirmed product facts**

Examples of prohibited statements:
- ❌ "The Basic Family Plan covers dental with 80% coinsurance."
- ❌ "Your Premium Individual Plan has a $500 deductible."
- ❌ "The Economy Plan does not include maternity coverage."
- ❌ "Corporate Group Plan copay is $25 for primary care."
- ❌ "The Starter Plan covers 100% preventive care."

### Why Prohibited

**Reason:** All Plans chunks in Phase 1 are placeholders awaiting final product specifications. Stating placeholder details as facts creates:
- **Legal liability** if placeholder data is inaccurate
- **Customer misinformation** leading to incorrect expectations
- **Financial risk** if customers make decisions based on incorrect benefit information
- **Compliance violations** if statements contradict actual policy terms

### What is Allowed

The prototype **CAN**:

✅ **Recognize plan names mentioned in queries** (context awareness)
✅ **Provide general benefit category explanations** (from FAQ/Rules)
✅ **Explain how benefits typically work** (from FAQ/Rules)
✅ **Direct users to verify plan-specific details** (with disclaimers)

Examples of allowed statements:
- ✅ "Dental coverage varies by plan type and tier. For your Basic Family Plan's specific dental coverage, please check your policy documents or contact customer service."
- ✅ "Deductible amounts vary by plan. To find your Premium Individual Plan's deductible, review your policy documents or log into your member portal."
- ✅ "Most plans include some maternity coverage, but coverage levels vary. Check your Economy Plan's benefits summary for specific maternity coverage details."

### Enforcement Mechanism

**Detection:**
- If answer contains plan name + specific benefit/cost/coverage detail from placeholder → **FLAG AS VIOLATION**
- If placeholder chunk score > 0.5 → **FLAG FOR REVIEW**
- If confidence_tier = Tier 3 but no disclaimer added → **FLAG AS VIOLATION**

**Action:**
- Block answer generation
- Generate safe fallback response
- Log violation for review
- Alert testing team

---

## Exclusion 2: Network Status Confirmation

### What is Prohibited

The prototype **must NOT**:

❌ **Confirm provider network status from placeholder data**

Examples of prohibited statements:
- ❌ "Yes, Dr. Ahmed is in-network."
- ❌ "Dubai Medical Center is covered under your plan."
- ❌ "You can see Dr. Sarah without out-of-network charges."
- ❌ "Al Zahra Hospital is in-network for your Corporate Plan."
- ❌ "This pharmacy is part of our network."

### Why Prohibited

**Reason:** All Network chunks in Phase 1 are placeholders awaiting confirmed provider contracts. Confirming network status from placeholders creates:
- **Financial risk** if patient receives care thinking it's in-network when it's not
- **Customer dissatisfaction** when billed for out-of-network services
- **Legal liability** if patient relied on incorrect network information
- **Provider relationship issues** if providers are incorrectly listed

### What is Allowed

The prototype **CAN**:

✅ **Recognize provider/facility names mentioned in queries**
✅ **Explain the network verification process** (from FAQ)
✅ **Explain in-network vs out-of-network differences** (from Rules)
✅ **Direct users to verify network status before appointment** (mandatory)

Examples of allowed statements:
- ✅ "To verify if Dr. Ahmed is in your network, call customer service at [number] with the provider's name and location."
- ✅ "Provider network status can change. Verify with customer service or use the online provider directory before scheduling your appointment."
- ✅ "In-network providers have contracted rates with the insurance company. Always verify network status before receiving services to avoid unexpected costs."

### Enforcement Mechanism

**Detection:**
- If answer contains provider/facility name + \"in-network\"/\"covered\"/\"included\" from placeholder → **FLAG AS VIOLATION**
- If network placeholder chunk score > 0.5 → **FLAG FOR REVIEW**
- If network query but no verification disclaimer → **FLAG AS VIOLATION**

**Action:**
- Block answer generation
- Generate network verification process response
- Log violation
- Alert testing team

---

## Exclusion 3: Cost and Pricing Claims

### What is Prohibited

The prototype **must NOT**:

❌ **State specific costs, copays, deductibles, or coinsurance from placeholders**

Examples of prohibited statements:
- ❌ "Your copay is $30 for specialist visits."
- ❌ "The deductible for your plan is $1,000."
- ❌ "Coinsurance is 20% for major procedures."
- ❌ "Out-of-pocket maximum is $5,000 annually."
- ❌ "Prescription copay is $15 for generic drugs."

### Why Prohibited

**Reason:** Placeholder cost data may not reflect final pricing. Stating placeholder costs as facts creates:
- **Financial expectations** that may be incorrect
- **Legal liability** if customers rely on incorrect pricing
- **Budgeting errors** for customers planning healthcare expenses
- **Customer dissatisfaction** when billed different amounts

### What is Allowed

The prototype **CAN**:

✅ **Explain cost-sharing concepts generally** (deductible, copay, coinsurance definitions)
✅ **Explain typical cost ranges** (\"copays typically range from $20-$75\")
✅ **Direct users to verify plan-specific costs** (with disclaimers)

Examples of allowed statements:
- ✅ "Copay amounts vary by plan type and provider category. For your specific copay amounts, check your policy documents or contact customer service."
- ✅ "Deductibles typically range from $500 to $5,000 depending on plan tier. To find your exact deductible, review your benefits summary or log into your member portal."
- ✅ "Cost-sharing (copays, deductibles, coinsurance) varies by plan. Contact customer service at [number] for specific pricing information."

### Enforcement Mechanism

**Detection:**
- If answer contains specific dollar amounts from placeholder → **FLAG AS VIOLATION**
- If cost query but only placeholder sources → **FLAG FOR REVIEW**
- If cost-related answer without pricing disclaimer → **FLAG AS VIOLATION**

**Action:**
- Block answer generation
- Generate general cost concept response with verification disclaimer
- Log violation
- Alert testing team

---

## Exclusion 4: Claims Adjudication

### What is Prohibited

The prototype **must NOT**:

❌ **Make claim approval or denial decisions**
❌ **Predict claim outcomes**
❌ **State whether specific claims will be paid**

Examples of prohibited statements:
- ❌ "Your claim will be approved."
- ❌ "This claim will be denied because..."
- ❌ "You are entitled to $500 reimbursement for this claim."
- ❌ "This service is not claimable under your plan."
- ❌ "Submit a claim for $1,200 and you'll receive payment within 2 weeks."

### Why Prohibited

**Reason:** Claims adjudication requires:
- Real-time policy verification
- Individual member eligibility checks
- Service medical necessity reviews
- Authorization verification
- Provider contract verification
- Detailed claim documentation review

The prototype has **none of these capabilities** in Phase 1.

### What is Allowed

The prototype **CAN**:

✅ **Explain the claims filing process** (from FAQ)
✅ **Explain claims processing timelines generally** (from FAQ)
✅ **Explain what documentation is typically required** (from FAQ)
✅ **Direct users to contact claims department for specific claim questions**

Examples of allowed statements:
- ✅ "To file a claim, submit an itemized bill and completed claim form via the member portal, email, or mail. Claims are typically processed within 15-30 business days."
- ✅ "For questions about a specific claim status, contact the claims department at [number] with your claim number."
- ✅ "Claim reimbursement amounts depend on your plan's coverage levels, deductible, and service details. The claims team will provide detailed information once your claim is reviewed."

### Enforcement Mechanism

**Detection:**
- If query asks for claim approval/denial prediction → **CLASSIFY AS UNSUPPORTED**
- If query asks for specific claim status → **CLASSIFY AS ACCOUNT-SPECIFIC**
- If answer attempts to predict claim outcome → **FLAG AS VIOLATION**

**Action:**
- Generate safe fallback: "For specific claim questions, contact claims department at [number]"
- Log violation
- Alert testing team

---

## Exclusion 5: Underwriting Decisions

### What is Prohibited

The prototype **must NOT**:

❌ **Make coverage eligibility decisions**
❌ **Approve or deny enrollment**
❌ **Determine if pre-existing conditions are covered**
❌ **Make plan recommendation decisions**

Examples of prohibited statements:
- ❌ "You are eligible for the Premium Plan."
- ❌ "Your pre-existing condition is covered."
- ❌ "You should choose the Basic Family Plan."
- ❌ "You cannot enroll because of your medical history."
- ❌ "Your application will be approved."

### Why Prohibited

**Reason:** Underwriting decisions require:
- Detailed medical history review
- Individual risk assessment
- Compliance with underwriting guidelines
- Regulatory compliance verification
- Human underwriter judgment

The prototype has **none of these capabilities**.

### What is Allowed

The prototype **CAN**:

✅ **Explain general enrollment process** (from FAQ)
✅ **Explain pre-existing condition disclosure requirements generally** (from Rules)
✅ **Explain plan comparison factors** (from FAQ)
✅ **Direct users to speak with enrollment specialists for personalized guidance**

Examples of allowed statements:
- ✅ "The enrollment process requires completing an application, disclosing pre-existing conditions, and selecting a plan tier. For personalized enrollment guidance, contact enrollment services at [number]."
- ✅ "Pre-existing conditions must be disclosed during enrollment. For questions about how your specific health history affects coverage, speak with an enrollment specialist."
- ✅ "Plan selection depends on your healthcare needs, budget, and family situation. Schedule a consultation with a benefits advisor to discuss which plan is right for you."

### Enforcement Mechanism

**Detection:**
- If query asks for eligibility decision → **CLASSIFY AS UNSUPPORTED**
- If query asks for pre-existing condition coverage decision → **FLAG FOR COMPLIANCE REVIEW**
- If answer attempts to make eligibility statement → **FLAG AS VIOLATION**

**Action:**
- Generate safe fallback: "For enrollment and eligibility questions, contact enrollment services at [number]"
- Log violation
- Alert testing team

---

## Exclusion 6: Legal/Compliance Advice

### What is Prohibited

The prototype **must NOT**:

❌ **Provide binding legal advice**
❌ **Interpret compliance regulations definitively**
❌ **Make legal recommendations**
❌ **Claim to replace legal counsel**

Examples of prohibited statements:
- ❌ "You are legally required to..."
- ❌ "This violates insurance regulations."
- ❌ "You could face legal penalties if..."
- ❌ "According to insurance law, you must..."
- ❌ "This is the correct legal interpretation..."

### Why Prohibited

**Reason:** Legal and compliance matters require:
- Professional legal counsel
- Regulatory expertise
- Individual case analysis
- Current regulatory knowledge
- Qualified legal professionals

The prototype is **not qualified** to provide legal or compliance advice.

### What is Allowed

The prototype **CAN**:

✅ **Explain general policy requirements** (from Rules, with caution disclaimer)
✅ **Explain disclosure obligations generally** (from Rules)
✅ **Direct users to compliance team for compliance questions**
✅ **Direct users to legal counsel for legal questions**

Examples of allowed statements:
- ✅ "Policy generally requires disclosure of pre-existing conditions during enrollment. For personalized guidance about disclosure requirements, contact the compliance team or your benefits advisor."
- ✅ "This is a compliance matter. For personalized guidance, consult your policy documents or contact the compliance team at [number]."
- ✅ "For legal questions about insurance regulations or your rights, consult with a qualified insurance attorney or your company's legal department."

### Enforcement Mechanism

**Detection:**
- If query contains \"legal\", \"law\", \"regulation\", \"compliance\" → **ADD CAUTION DISCLAIMER**
- If Rules status = \"Needs Review\" + compliance topic → **MANDATORY DISCLAIMER**
- If answer attempts to provide definitive legal interpretation → **FLAG AS VIOLATION**

**Action:**
- Add mandatory disclaimer: "This is a compliance matter. For personalized guidance, contact compliance team."
- If legal question → direct to legal counsel
- Log for compliance review

---

## Exclusion 7: Medical Advice

### What is Prohibited

The prototype **must NOT**:

❌ **Provide medical diagnosis**
❌ **Recommend medical treatments**
❌ **Interpret medical conditions**
❌ **Suggest whether medical care is necessary**

Examples of prohibited statements:
- ❌ "You should see a doctor for that."
- ❌ "That sounds like [medical condition]."
- ❌ "You need to get [medical test/treatment]."
- ❌ "That is a medical emergency."
- ❌ "You don't need to see a specialist for that."

### Why Prohibited

**Reason:** Medical advice requires:
- Medical professional qualifications
- Individual patient assessment
- Medical history review
- Licensed healthcare provider

The prototype is **not a medical professional** and cannot provide medical advice.

### What is Allowed

The prototype **CAN**:

✅ **Explain which benefit categories cover which service types** (from FAQ/Rules)
✅ **Explain pre-authorization requirements for services** (from Rules)
✅ **Direct users to consult healthcare providers for medical questions**

Examples of allowed statements:
- ✅ "For questions about whether you need medical care, consult your healthcare provider."
- ✅ "Emergency services are generally covered, but it's important to seek immediate medical attention for any medical emergency rather than checking coverage first."
- ✅ "Specialist referrals may require pre-authorization depending on your plan. Contact customer service to verify authorization requirements, but consult your doctor about whether specialist care is medically appropriate for your situation."

### Enforcement Mechanism

**Detection:**
- If query asks for medical advice → **CLASSIFY AS OUT OF SCOPE**
- If answer attempts medical diagnosis/recommendation → **FLAG AS VIOLATION**

**Action:**
- Generate safe fallback: "For medical questions, consult your healthcare provider."
- Log violation
- Alert testing team

---

## Exclusion 8: Account Operations

### What is Prohibited

The prototype **must NOT**:

❌ **Perform account transactions**
❌ **Modify account information**
❌ **Access individual member data**
❌ **Process payments**
❌ **Submit claims on behalf of members**
❌ **Make plan changes**

Examples of prohibited actions:
- ❌ Filing a claim for the user
- ❌ Changing plan selection
- ❌ Adding/removing dependents
- ❌ Processing payments
- ❌ Updating contact information
- ❌ Resetting passwords
- ❌ Checking specific claim status
- ❌ Checking deductible balance

### Why Prohibited

**Reason:** Account operations require:
- Secure authentication
- Authorization verification
- Transactional systems (not available in prototype)
- Audit trails
- Data security compliance

The prototype is **read-only knowledge retrieval** only.

### What is Allowed

The prototype **CAN**:

✅ **Explain how to perform account operations** (from FAQ)
✅ **Direct users to member portal or customer service to perform operations**

Examples of allowed statements:
- ✅ "To file a claim, log into the member portal at [url] or contact customer service at [number]."
- ✅ "To add a dependent, log into your account, navigate to 'My Family', and follow the enrollment steps. Or contact customer service for assistance."
- ✅ "For account-specific information like claim status or deductible balance, log into your member portal or contact customer service."

### Enforcement Mechanism

**Detection:**
- If query asks to perform transaction → **CLASSIFY AS UNSUPPORTED**
- If query asks for account-specific data → **CLASSIFY AS ACCOUNT-SPECIFIC**

**Action:**
- Generate safe fallback directing to member portal or customer service
- Log request
- Do NOT attempt to access member data

---

## Exclusion 9: Policy Document Replacement

### What is Prohibited

The prototype **must NOT**:

❌ **Claim to replace official policy documents**
❌ **State that KB content is legally binding**
❌ **Contradict policy documents**
❌ **Claim to be authoritative source of policy truth**

Examples of prohibited statements:
- ❌ "This answer replaces your policy documents."
- ❌ "You don't need to read your policy, I've told you everything."
- ❌ "This is the official policy."
- ❌ "My answer is legally binding."
- ❌ "Trust this answer instead of your policy documents."

### Why Prohibited

**Reason:** Official policy documents are:
- **Legally binding contracts** between insurer and member
- **Regulatory compliance documents** subject to insurance law
- **Authoritative source of truth** for coverage disputes
- **Individualized to each member's plan and enrollment**

The prototype KB is:
- **General guidance** based on common patterns
- **Not a legal contract**
- **Not individualized** to specific members
- **Subject to errors and incompleteness**

### What is Allowed

The prototype **CAN**:

✅ **Provide general guidance based on KB content**
✅ **Direct users to policy documents for authoritative information**
✅ **Acknowledge that policy documents are the final authority**

Examples of allowed statements:
- ✅ "This answer provides general guidance. For authoritative information specific to your plan, refer to your policy documents or contact customer service."
- ✅ "If there's a discrepancy between this answer and your policy documents, your policy documents govern."
- ✅ "For legally binding coverage details, review your policy documents or contact customer service."

### Enforcement Mechanism

**Detection:**
- All answers should include implicit acknowledgment that policy documents are authoritative
- If query asks if KB replaces policy → **CLASSIFY AS OUT OF SCOPE**

**Action:**
- Generate safe response: "This KB provides general guidance. Your policy documents are the authoritative source for your coverage. If there's a discrepancy, your policy documents govern."
- Log query
- Review for improvements to FAQ wording

---

## Exclusion Summary Table

| Exclusion | What NOT to Do | Why Prohibited | What IS Allowed | Violation Severity |
|-----------|----------------|----------------|-----------------|-------------------|
| **Plan Benefits** | State placeholder plan details as facts | Legal liability, customer misinformation | Recognize plan names, provide general guidance, require verification | **CRITICAL** |
| **Network Status** | Confirm provider network status from placeholders | Financial risk, customer dissatisfaction | Explain verification process, recognize provider names, require verification | **CRITICAL** |
| **Cost/Pricing** | State specific costs from placeholders | Financial expectations, legal liability | Explain cost concepts, provide ranges, require verification | **CRITICAL** |
| **Claims Adjudication** | Make claim approval/denial decisions | Requires real-time systems and human review | Explain claims process, direct to claims department | **HIGH** |
| **Underwriting** | Make eligibility/enrollment decisions | Requires medical review and human judgment | Explain enrollment process, direct to enrollment services | **HIGH** |
| **Legal/Compliance** | Provide binding legal advice | Requires qualified legal counsel | Explain general requirements, direct to compliance team, add caution disclaimer | **HIGH** |
| **Medical Advice** | Provide medical diagnosis/treatment recommendations | Requires licensed healthcare provider | Explain benefit coverage, direct to healthcare provider | **MEDIUM** |
| **Account Operations** | Perform transactions or access member data | Requires secure systems and authorization | Explain how to perform operations, direct to portal/service | **MEDIUM** |
| **Policy Replacement** | Claim KB replaces policy documents | Policy documents are legal contracts | Provide general guidance, acknowledge policy documents govern | **MEDIUM** |

---

## Monitoring for Exclusion Violations

During internal testing, actively monitor for:

1. **Placeholder Leakage:**
   - Any answer stating placeholder details as facts
   - Any network status confirmation from placeholders
   - Any cost/pricing from placeholders

2. **Inappropriate Certainty:**
   - Claim adjudication predictions
   - Eligibility decisions
   - Legal interpretations without disclaimers

3. **Medical Advice:**
   - Medical diagnosis language
   - Treatment recommendations
   - Medical necessity judgments

4. **Account Operations:**
   - Attempts to access member data
   - Attempts to perform transactions

5. **Policy Replacement Claims:**
   - Language suggesting KB replaces policy documents
   - Language claiming KB is legally binding

---

## Violation Response Protocol

When exclusion violation detected:

**Severity: CRITICAL (Plan, Network, Cost)**
1. **Block answer generation immediately**
2. Generate safe fallback response
3. **Alert testing team immediately**
4. Log violation with full trace
5. Review filtering/weighting to prevent recurrence
6. **Do not allow prototype to proceed** until violation fixed

**Severity: HIGH (Claims, Underwriting, Legal)**
1. Block answer generation
2. Generate safe fallback directing to appropriate department
3. Log violation
4. Review weekly, adjust if pattern emerges

**Severity: MEDIUM (Medical, Account, Policy)**
1. Generate appropriate fallback response
2. Log violation
3. Review monthly, adjust if pattern emerges

---

## Implementation Notes for Engineering

### Detection Mechanisms

**Placeholder Leakage Detection:**
```python
def detect_placeholder_leakage(answer_text, sources):
    # Check if any placeholder chunks used
    placeholders = [s for s in sources if s['is_placeholder'] == True]
    
    if not placeholders:
        return False  # No placeholders, no leakage risk
    
    for placeholder in placeholders:
        # Extract specific details from placeholder content
        details = extract_specific_details(placeholder['content'])
        
        for detail in details:
            if detail in answer_text:
                # VIOLATION: Placeholder detail stated in answer
                return True
    
    return False
```

**Inappropriate Certainty Detection:**
```python
def detect_inappropriate_certainty(query, answer_text):
    claim_keywords = ["will be approved", "will be denied", "you are eligible", 
                      "you cannot enroll", "is covered", "is not covered"]
    
    for keyword in claim_keywords:
        if keyword in answer_text.lower():
            # Check if appropriate disclaimers present
            if not has_appropriate_disclaimers(answer_text):
                return True  # VIOLATION: Inappropriate certainty
    
    return False
```

### Safe Fallback Responses

**Plan-Specific Fallback:**
```
"For specific details about your plan benefits, please check your policy 
documents or contact customer service at [number]. I can provide general 
information about how benefits typically work."
```

**Network-Specific Fallback:**
```
"To verify provider network status, please contact customer service at [number] 
or use the online provider directory. Provider network status may change, so 
always verify before scheduling appointments."
```

**Cost-Specific Fallback:**
```
"For specific cost information, please check your policy documents or contact 
customer service at [number]. Costs vary by plan type, service category, and 
other factors."
```

**Claims/Underwriting/Account Fallback:**
```
"For questions about specific claims, eligibility, or account information, please 
contact customer service at [number] who can access your account details and 
provide personalized assistance."
```

---

## Document Control

**Filename:** PROTOTYPE_EXCLUSIONS.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_SCOPE.md - What is in/out of scope
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Answer generation rules
- PROTOTYPE_TEST_QUERIES.md - Test query set (next)
- INTERNAL_TESTING_PLAN.md - Testing approach (next)
- HANDOFF_TO_ENGINEERING.md - Implementation handoff

---

**END OF EXCLUSIONS SPECIFICATION**
