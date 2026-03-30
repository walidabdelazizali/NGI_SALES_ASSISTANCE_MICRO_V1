# Placeholder Enforcement Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define strict operational rules for placeholder chunk handling

---

## 1. Overview

This specification defines **strict enforcement rules** to prevent placeholder chunks from being misrepresented as confirmed product/provider truth.

### Critical Context

**Current State:**
- 10 Plan placeholder chunks (PLAN-001 through PLAN-010)
- 10 Network placeholder chunks (PROV-001 through PROV-010)
- **Total:** 20 placeholder chunks (23% of total KB)
- **Status:** ALL "Pending Detail"
- **is_placeholder:** ALL true
- **safe_for_client_direct_use:** ALL false

**Placeholder Purpose:**
- Structural scaffolding for future real data
- Question routing and context awareness
- Gap identification for content planning
- NOT confirmed product benefits or provider directory

**Placeholder Risk:**
- **Legal Liability:** CRITICAL - Stating placeholder as fact could lead to litigation
- **Customer Misinformation:** HIGH - Damages customer trust and relationships
- **Regulatory Violations:** CRITICAL - Misleading product/provider information

---

## 2. Fundamental Enforcement Rules

### Rule 1: Placeholders Are NOT Confirmed Truth (NON-NEGOTIABLE)

**Policy:**
Plans and Network placeholders **MUST NEVER** be presented as confirmed insurance product benefits or verified provider network status.

**All placeholder chunks have:**
- `is_placeholder: true`
- `status: "Pending Detail"`
- Embedded warning text: "IMPORTANT: This is a structural placeholder..."
- `safe_for_client_direct_use: false`
- `retrieval_weight_hint: 0.2` (very low)

**Enforcement:**
- MANDATORY filtering for customer-facing retrieval (exclude is_placeholder=true)
- OR heavy disclaimers if context awareness needed

---

### Rule 2: FAQ and Rules ALWAYS Override Placeholders (NON-NEGOTIABLE)

**Policy:**
If retrieval returns both FAQ/Rules AND placeholder content, answer generation **MUST** prioritize FAQ/Rules. Placeholder content may provide context but NEVER contradicts or overrides FAQ/Rules.

**Enforcement:**
- Retrieval weighting ensures FAQ (1.0) and Rules (0.9) score much higher than placeholders (0.2)
- Answer generation logic checks is_placeholder flag, defers to non-placeholder sources

---

### Rule 3: Placeholder Identification is Mandatory (NON-NEGOTIABLE)

**Policy:**
Every chunk MUST be correctly tagged with `is_placeholder` flag during ingestion. Missing or incorrect flag = deployment blocker.

**Enforcement:**
- Pre-deployment validation checks ALL Plans chunks have `is_placeholder: true`
- Pre-deployment validation checks ALL Network chunks have `is_placeholder: true`
- Pre-deployment validation checks ALL FAQ/Rules/Mapping have `is_placeholder: false`

---

## 3. Allowed Use Cases for Placeholders

### ✅ Use Case 1: Question Routing

**Purpose:** Recognize question intent and route appropriately

**Example:**
```
User Query: "What does the Basic Family Plan cover?"

Placeholder Usage (ALLOWED):
- System recognizes "Basic Family Plan" (from PLAN-003 context)
- System identifies this as a plan-specific question
- System routes to appropriate response strategy

Answer Generated:
"For specific coverage details about the Basic Family Plan, please check your 
policy documents or contact customer service at [number]."
```

**Why Allowed:** Placeholder provides routing awareness, but does NOT provide answer content. Answer defers to authoritative sources.

---

### ✅ Use Case 2: Context Awareness

**Purpose:** Understand user's context without confirming specifics

**Example:**
```
User Query: "I have a Basic Family Plan. How do I file a claim?"

Placeholder Usage (ALLOWED):
- System recognizes "Basic Family Plan" (from PLAN-003)
- System understands user has a family plan type
- System provides general claims guidance

Answer Generated:
"To file a claim: [general claims process from FAQ/Rules]

For plan-specific claim requirements for your Basic Family Plan, 
please refer to your policy documents."
```

**Why Allowed:** Placeholder provides context (family plan type) but answer content comes from FAQ/Rules. Plan-specific details deferred.

---

### ✅ Use Case 3: Gap Identification

**Purpose:** Analytics and content planning

**Example:**
```
Analytics Report:
"Top 10 unanswerable questions this month:
- 5 questions about Basic Family Plan benefits (PLAN-003 is placeholder)
- 3 questions about Dubai Medical Center network status (PROV-001 is placeholder)

Recommendation: Prioritize obtaining real data for PLAN-003 and PROV-001."
```

**Why Allowed:** Placeholder used internally for analytics, not customer-facing answers.

---

### ✅ Use Case 4: Future Data Preparation

**Purpose:** Design data pipeline and ingestion process

**Example:**
```
Data Engineering Task:
"Design ingestion process to replace PLAN-003 placeholder with real 
Basic Family Plan product documentation. Ensure:
- is_placeholder changed from true to false
- retrieval_weight_hint updated from 0.2 to 0.9
- safe_for_client_direct_use changed from false to true
- deprecated_date set on old placeholder
- superseded_by links old to new"
```

**Why Allowed:** Placeholder used as template for future real data, not customer answers.

---

### ✅ Use Case 5: Mapping Cross-Reference

**Purpose:** Prepare for future FAQ-Rule-Plan relationships

**Example:**
```
Mapping Chunk (MAP-005):
"Question: Does my plan cover dental? (FAQ-005)
Primary Rule: RULE-003 (Benefit Categories)
Related Plan: PLAN-003 (Basic Family Plan - PLACEHOLDER)
...
This FAQ requires plan-specific confirmation."
```

**Why Allowed:** Mapping establishes relationship structure for when real plan data arrives. Clearly marked as requiring plan confirmation.

---

## 4. Forbidden Use Cases for Placeholders

### ❌ Forbidden Use Case 1: Stating Placeholder as Fact

**BAD Example:**
```
User Query: "What does the Basic Family Plan cover?"

WRONG Answer:
"The Basic Family Plan covers outpatient consultations, inpatient hospitalization, 
and emergency care. [sourced from PLAN-003 placeholder]"
```

**Why Dangerous:**
- Presents placeholder as confirmed product benefits
- Legal liability if customer makes enrollment decisions based on placeholder
- Regulatory violation (misleading product information)

**Consequences:**
- Customer enrolls expecting coverage that may not exist
- Customer files claim that's denied
- Customer sues for misrepresentation
- Regulatory penalties

**CORRECT Answer:**
```
"For specific coverage details about the Basic Family Plan, please check your 
policy documents or contact customer service at [number]. Coverage varies by 
plan, and I want to make sure you have accurate information for your specific plan."
```

---

### ❌ Forbidden Use Case 2: Confirming Provider Network Status

**BAD Example:**
```
User Query: "Is Dubai Medical Center in-network?"

WRONG Answer:
"Yes, Dubai Medical Center is in our Premium Network. [sourced from PROV-001 placeholder]"
```

**Why Dangerous:**
- Confirms network status based on unverified placeholder
- Customer schedules appointment assuming in-network
- Customer incurs out-of-network costs
- Legal liability for incorrect network information

**Consequences:**
- Customer receives unexpected bill (out-of-network rates)
- Customer complaints and negative reviews
- Loss of customer trust
- Potential litigation

**CORRECT Answer:**
```
"To verify whether Dubai Medical Center is in-network for your plan, please check 
our online provider directory at [URL] or contact customer service at [number] 
before scheduling your appointment. Provider network participation can change, 
so it's important to verify before your visit."
```

---

### ❌ Forbidden Use Case 3: Comparing Plans

**BAD Example:**
```
User Query: "What's the difference between Basic and Premium Plan?"

WRONG Answer:
"The Basic Plan costs AED 400/month with AED 500 deductible, while the Premium 
Plan costs AED 800/month with AED 200 deductible. [sourced from PLAN-001 and PLAN-002 placeholders]"
```

**Why Dangerous:**
- Compares placeholder costs as if real product data
- Customer makes enrollment decision based on placeholder
- Legal liability if actual costs differ significantly

**Consequences:**
- Customer selects plan thinking it costs AED 400, actual cost is AED 600
- Customer budget shortfall
- Customer disputes charges
- Regulatory violation (misleading pricing)

**CORRECT Answer:**
```
"Plan coverage and costs vary depending on your specific plan type and options. 
For detailed plan comparison including costs, benefits, and coverage, please:
- Visit our plan comparison tool at [URL]
- Contact our sales team at [number]
- Review plan brochures at [URL]

I can help you understand general insurance concepts like deductibles and copays."
```

---

### ❌ Forbidden Use Case 4: Calculating Costs

**BAD Example:**
```
User Query: "How much will my doctor visit cost?"

WRONG Answer:
"With your Basic Individual Plan, your copay will be AED 50 per visit. 
[sourced from PLAN-001 placeholder]"
```

**Why Dangerous:**
- States placeholder copay as actual cost
- Customer budgets based on placeholder
- Actual cost may differ significantly

**Consequences:**
- Customer expects AED 50, charged AED 100
- Customer cannot afford treatment
- Customer complaints
- Legal liability

**CORRECT Answer:**
```
"Cost for doctor visits varies by plan and provider. Your copay amount is 
listed in your policy documents. 

To find your specific copay:
- Check your insurance card or policy documents
- Contact customer service at [number]
- Log into your member portal

I can explain what a copay is and how it works in general."
```

---

### ❌ Forbidden Use Case 5: Displaying Placeholder Directly

**BAD Example:**
```
User Query: "What plans do you offer?"

WRONG Answer:
"We offer these plans:
- Basic Individual Plan (AED 400/month) [PLAN-001 placeholder]
- Basic Family Plan (AED 600/month) [PLAN-003 placeholder]
- Premium Corporate Plan (AED 1200/month) [PLAN-010 placeholder]
..."
```

**Why Dangerous:**
- Lists placeholder plans as confirmed product portfolio
- Includes placeholder pricing as actual costs
- Customers may try to enroll in non-existent plans

**Consequences:**
- Customer attempts to enroll in placeholder plan
- Enrollment process breaks or shows different pricing
- Customer confusion and frustration
- Loss of trust

**CORRECT Answer:**
```
"We offer a range of health insurance plans for individuals, families, groups, 
and corporate clients. 

To explore our current plan options and pricing:
- Visit our plans page at [URL]
- Contact our sales team at [number]
- Schedule a consultation

I can help you understand plan features like deductibles, copays, and coverage types."
```

---

### ❌ Forbidden Use Case 6: Over-Weighting in Retrieval

**BAD Scenario:**
```
Retrieval Configuration:
- FAQ: weight = 0.5
- Plans Placeholder: weight = 0.8  ← WRONG!!!
```

**Why Dangerous:**
- Placeholders outrank FAQ in retrieval
- Increases likelihood of placeholder content appearing in answers
- Violates trust hierarchy

**Consequences:**
- Placeholder content dominates retrieved results
- Higher risk of presenting placeholder as fact
- Degraded answer quality (weaker sources prioritized)

**CORRECT Configuration:**
```
Retrieval Configuration:
- FAQ: weight = 1.0
- Rules: weight = 0.9
- Mapping: weight = 0.4-0.6
- Plans Placeholder: weight = 0.2  ← CORRECT
```

---

## 5. Enforcement Mechanisms

### Mechanism 1: Pre-Ingestion Validation

**Check:** All Plans/Network chunks tagged correctly

```python
def validate_placeholder_tagging(chunks):
    for chunk in chunks:
        if chunk['chunk_type'] in ['Plans', 'Network']:
            assert chunk['is_placeholder'] == True, \
                f"Chunk {chunk['chunk_id']} missing is_placeholder flag!"
            assert chunk['safe_for_client_direct_use'] == False, \
                f"Chunk {chunk['chunk_id']} incorrectly marked safe!"
            assert chunk['retrieval_weight_hint'] <= 0.3, \
                f"Chunk {chunk['chunk_id']} weight too high ({chunk['retrieval_weight_hint']})!"
```

**Deployment Gate:** MUST pass before ingestion

---

### Mechanism 2: Runtime Filtering

**Check:** Customer-facing retrieval excludes placeholders

```python
def retrieve_for_customer(query, top_k=10):
    filter_conditions = {
        "is_placeholder": False,  # ← Mandatory for customer-facing
    }
    results = vector_db.query(query, filter=filter_conditions, top_k=top_k)
    return results
```

**Enforcement:** Code review + automated testing

---

### Mechanism 3: Answer Generation Guards

**Check:** Answer does not cite placeholder as source of truth

```python
def generate_answer(query, retrieved_chunks):
    # Filter out placeholders from answer sources
    answer_sources = [c for c in retrieved_chunks if not c['is_placeholder']]
    
    # If only placeholders retrieved (should be rare due to filtering)
    if len(answer_sources) == 0:
        return "I need to connect you with customer service for accurate information about your specific plan. [Contact info]"
    
    # Generate answer from non-placeholder sources only
    answer = llm.generate(query, answer_sources)
    
    # Add disclaimers if plan/network-specific question
    if requires_plan_confirmation(query, answer_sources):
        answer += "\n\n⚠️ Check your policy documents for plan-specific details."
    
    return answer
```

**Enforcement:** Code review + test scenarios

---

### Mechanism 4: Automated Leak Detection

**Check:** Monitor for placeholder content in customer answers

```python
def detect_placeholder_leak(answer, sources):
    for source in sources:
        if source['is_placeholder'] == True:
            alert("🚨 PLACEHOLDER LEAK DETECTED!")
            log_incident({
                "answer": answer,
                "placeholder_source": source['chunk_id'],
                "timestamp": datetime.now()
            })
            return True
    return False
```

**Enforcement:** Real-time monitoring + alerts

---

### Mechanism 5: Periodic Audits

**Check:** Sample customer interactions, verify no placeholder leaks

```python
def audit_customer_interactions(sample_size=100):
    interactions = get_recent_interactions(sample_size)
    leaks = []
    
    for interaction in interactions:
        for source in interaction['sources']:
            if source['is_placeholder'] == True:
                leaks.append(interaction)
    
    report = {
        "total_sampled": sample_size,
        "leaks_detected": len(leaks),
        "leak_rate": len(leaks) / sample_size,
    }
    
    if report['leak_rate'] > 0:
        escalate_to_compliance(report, leaks)
    
    return report
```

**Enforcement:** Quarterly audits + compliance review

---

## 6. Placeholder Replacement Process

### When Real Data Arrives

**Trigger:** Real plan data or provider network data becomes available

**Example:** Real "Basic Family Plan" product documentation approved

**Process:**

**Step 1: Create New Chunk with Real Data**
```json
{
  "chunk_id": "PLAN-CHUNK-103",
  "chunk_type": "Plans",
  "source_id": "PLAN-103",
  "plan_id": "PLAN-103",
  "plan_name": "Basic Family Plan",
  "text": "Basic Family Plan\nMonthly Premium: AED 550\nDeductible: AED 500\nCoverage: Outpatient, Inpatient, Emergency, Prescription Drugs...",
  "status": "Active",
  "is_placeholder": false,  ← CRITICAL CHANGE
  "safe_for_client_direct_use": true,  ← Now safe
  "retrieval_weight_hint": 0.9,  ← Much higher than 0.2
  "supersedes": "PLAN-003"  ← Link to old placeholder
}
```

---

**Step 2: Deprecate Old Placeholder**
```json
{
  "chunk_id": "PLAN-CHUNK-003",
  "source_id": "PLAN-003",
  "status": "Deprecated",  ← Mark as old
  "deprecated_date": "2026-09-15",
  "superseded_by": "PLAN-103"  ← Link to new
}
```

---

**Step 3: Update Mappings**
```json
{
  "chunk_id": "MAP-CHUNK-005",
  "question_id": "FAQ-005",
  "primary_rule_id": "RULE-003",
  "related_plan_id": "PLAN-103",  ← Updated from PLAN-003
  "updated_date": "2026-09-15"
}
```

---

**Step 4: Remove Old Placeholder from Active Retrieval**
- Filter out `status: "Deprecated"` in retrieval
- Archive old placeholder (keep for traceability, not active retrieval)
- Within 30 days of new chunk deployment

---

**Step 5: Validate Replacement**
- Test queries mentioning "Basic Family Plan"
- Verify PLAN-103 (real data) retrieved, not PLAN-003 (placeholder)
- Verify answer provides real plan details confidently
- Verify no disclaimers needed (real data = high confidence)

---

### Timeline

**Plans:** Expected within 6 months (depends on product finalization)
**Network:** Expected within 3 months (depends on provider contracts)

See RAG_POLICY_V1/PLACEHOLDER_HANDLING_POLICY.md for detailed timeline.

---

## 7. Monitoring and Alerting

### Alert 1: Placeholder Leak to Customer Answer
**Trigger:** Placeholder chunk appears in customer answer sources
**Severity:** CRITICAL
**Action:** Immediate investigation + answer correction + incident report

---

### Alert 2: Placeholder Weight Too High
**Trigger:** Placeholder `retrieval_weight_hint` > 0.3
**Severity:** HIGH
**Action:** Metadata correction + validation

---

### Alert 3: Placeholder Missing is_placeholder Flag
**Trigger:** Plans/Network chunk with `is_placeholder: false` or missing
**Severity:** CRITICAL
**Action:** Deployment blocked + metadata correction

---

### Alert 4: High Placeholder Retrieval Rate
**Trigger:** Placeholders appear in >10% of top-10 retrieval results
**Severity:** MEDIUM
**Action:** Review retrieval weights + FAQ/Rules content quality

---

## 8. Training and Documentation

### For Developers
**Key Messages:**
- "Placeholders are structural scaffolding, NOT real product/provider data"
- "Always filter `is_placeholder: true` for customer-facing retrieval"
- "FAQ and Rules ALWAYS override placeholders in answer generation"
- "Test placeholder leak scenarios before deployment"

---

### For Data Engineers
**Key Messages:**
- "All Plans/Network chunks MUST have `is_placeholder: true`"
- "Metadata validation is mandatory pre-deployment gate"
- "Placeholder replacement requires deprecation of old chunk + creation of new chunk"
- "Retrieval weights must maintain trust hierarchy"

---

### For QA Engineers
**Key Messages:**
- "Test scenarios where placeholder has better semantic match than FAQ"
- "Verify placeholder never appears in customer answer as source of truth"
- "Test plan-specific and network-specific questions for proper disclaimers"
- "Verify placeholder leak detection alerts work"

---

## 9. Compliance and Governance

### Quarterly Review
- Sample 100 customer interactions
- Verify 0% placeholder leak rate
- Review placeholder retrieval ranking (should be low)
- Check placeholder replacement progress

---

### Annual Review
- Comprehensive audit of all 87 chunks
- Verify placeholder metadata correctness
- Test enforcement mechanisms
- Update policy as needed

---

### Incident Reporting
If placeholder leak detected:
1. Immediate investigation (within 1 hour)
2. Answer correction (contact customer if needed)
3. Root cause analysis (within 24 hours)
4. Fix implementation (within 48 hours)
5. Validation testing (before re-deployment)
6. Incident report (to compliance team)

---

## 10. Success Criteria

**Placeholder enforcement is successful if:**
- ✅ 0% placeholder leak rate (no placeholders in customer answers as confirmed facts)
- ✅ All Plans/Network chunks correctly tagged with `is_placeholder: true`
- ✅ Placeholders rank very low in retrieval (typically >position 20)
- ✅ Trust hierarchy maintained (FAQ/Rules dominate)
- ✅ Customer questions about plans/network receive appropriate disclaimers
- ✅ No legal incidents related to placeholder misrepresentation

---

## 11. Document Control

**Filename:** PLACEHOLDER_ENFORCEMENT_SPEC.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- RAG_POLICY_V1/PLACEHOLDER_HANDLING_POLICY.md - Detailed policy rules
- CHUNK_FILTERING_RULES.md - Filtering implementation
- RETRIEVAL_WEIGHTING_SPEC.md - Weight enforcement
- ANSWER_SAFETY_BEHAVIOR.md - Answer generation with placeholders

---

**END OF PLACEHOLDER ENFORCEMENT SPECIFICATION**

**CRITICAL REMINDER:** Placeholders exist to prepare for future real data, NOT to provide customer answers.
