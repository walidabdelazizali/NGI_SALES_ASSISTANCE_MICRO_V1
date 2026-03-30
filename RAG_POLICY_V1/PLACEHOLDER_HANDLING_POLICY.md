# Placeholder Handling Policy - Micro Insurance KB V1

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define strict rules for handling placeholder plan and network chunks  
**Enforcement:** MANDATORY - Non-negotiable for production deployment

---

## 1. Executive Summary

The Micro Insurance KB V1 package contains **20 placeholder chunks** (10 plans + 10 network providers) that are **NOT confirmed business data**. These placeholders are structural scaffolding created to prepare for future real data.

**Critical Policy:**

🚨 **Placeholder chunks MUST NEVER be presented to customers as confirmed insurance facts.** 🚨

This policy defines:
- What placeholders are and why they exist
- What can be safely done with placeholders
- What must NEVER be done with placeholders
- How to replace placeholders with real data
- How to prevent placeholder content leaks

---

## 2. What Are Placeholders?

### Definition

**Placeholder:** A knowledge chunk that contains structural information (plan names, provider types, benefit categories) but lacks verified business data. Placeholders serve as scaffolding for future real data integration.

### Identification

All placeholder chunks have:
- `is_placeholder: true` flag
- `status: "Pending Detail"`
- `safe_for_client_direct_use: false` flag
- `retrieval_weight_hint: 0.2` (very low)
- Warning text in `text` field: "IMPORTANT: This is a structural placeholder..."

### Current Placeholder Inventory

**Plans Chunks:** 10 placeholders
- PLAN-001: Basic Individual Plan (placeholder)
- PLAN-002: Comprehensive Individual Plan (placeholder)
- PLAN-003: Basic Family Plan (placeholder)
- PLAN-004: Comprehensive Family Plan (placeholder)
- PLAN-005: Basic Group Plan (placeholder)
- PLAN-006: Comprehensive Group Plan (placeholder)
- PLAN-007: Premium Individual Plan (placeholder)
- PLAN-008: Premium Family Plan (placeholder)
- PLAN-009: Basic Corporate Plan (placeholder)
- PLAN-010: Premium Corporate Plan (placeholder)

**Network Chunks:** 10 placeholders
- PROV-001: Dubai Medical Center (hospital placeholder)
- PROV-002: Abu Dhabi General Hospital (hospital placeholder)
- PROV-003: Sharjah Clinic (clinic placeholder)
- PROV-004: Al Ain Pharmacy (pharmacy placeholder)
- PROV-005: Dubai Heart Specialist (specialist placeholder)
- PROV-006: Diagnostic Lab Services (lab placeholder)
- PROV-007: Emirates Clinic Network (clinic placeholder)
- PROV-008: Dubai Pharmacy Group (pharmacy placeholder)
- PROV-009: Regional Hospital Network (hospital placeholder)
- PROV-010: Specialist Medical Center (specialist placeholder)

---

## 3. Why Placeholders Exist

### Purpose

1. **Structural Preparation:** Establish plan and provider type taxonomy before real data arrives
2. **Routing Awareness:** Enable system to recognize plan-related and network-related questions
3. **Cross-Reference Scaffolding:** Allow mapping layer to reference future plan/network IDs
4. **Data Pipeline Testing:** Validate ingestion workflow before real data integration
5. **Gap Identification:** Highlight where real business data is still needed

### What Placeholders Are NOT

❌ Placeholders are NOT:
- Confirmed product definitions
- Live provider directories
- Approved benefit structures
- Verified network lists
- Ready for customer-facing answers

---

## 4. Critical Risks of Mishandling Placeholders

### Risk 1: Legal Liability

**Scenario:** Customer is told "Your Basic Individual Plan covers annual dental checkups" based on placeholder PLAN-003.

**Impact:** If real plan doesn't cover dental, customer has reliedon incorrect information. Company faces legal claims for misrepresentation.

**Severity:** 🔴 **CRITICAL** - Could result in litigation, financial claims, regulatory penalties.

---

### Risk 2: Customer Misinformation

**Scenario:** Customer schedules appointment at "Dubai Medical Center" believing it's in-network based on placeholder PROV-001.

**Impact:** Customer discovers provider is out-of-network, faces unexpected costs, loses trust in company.

**Severity:** 🔴 **HIGH** - Damages customer relationships, increases complaints, harms reputation.

---

### Risk 3: Regulatory Violations

**Scenario:** Insurance authority audits customer communications, discovers unverified benefit claims.

**Impact:** Regulatory fines, mandatory corrective actions, potential license suspension.

**Severity:** 🔴 **CRITICAL** - Could threaten business operations.

---

### Risk 4: Operational Confusion

**Scenario:** Customer service agents rely on placeholder data, provide inconsistent or incorrect guidance.

**Impact:** Operational chaos, staff frustration, increased escalations, poor customer experience.

**Severity:** 🟡 **MEDIUM** - Manageable but disruptive.

---

## 5. What You CAN Do with Placeholders

### ✅ Allowed Use Case 1: Question Routing

**Safe Use:** Recognize that a question is plan-related and requires plan-specific context.

**Example:**
```
User: "Does my plan cover vision care?"
System: Detects "plan cover" pattern
System: Retrieves FAQ, Rules, and identifies plan-dependency
System: Responds with general guidance + disclaimer
```

**Why Safe:** System doesn't state placeholder plan details, just routes appropriately.

---

### ✅ Allowed Use Case 2: Context Awareness

**Safe Use:** Understand plan type categories (Individual, Family, Group) for better routing.

**Example:**
```
User: "I have a family plan. Can I add my newborn?"
System: Recognizes "family plan" context
System: Retrieves RULE-006 (Dependent Addition)
System: Responds: "Yes, you can typically add a newborn during a special enrollment 
                  period. Please contact customer service to add your dependent."
```

**Why Safe:** Doesn't claim specific family plan benefits, uses general rule logic.

---

### ✅ Allowed Use Case 3: Gap Identification

**Safe Use:** Identify which plan-specific or network-specific questions cannot be fully answered.

**Example:**
```
Analytics: Question "What's my deductible for Plan X?" frequently asked
System: Identifies plan-specific detail gap
Action: Flag for real data acquisition
```

**Why Safe:** Internal analytics use, not customer-facing.

---

### ✅ Allowed Use Case 4: Future Data Preparation

**Safe Use:** Use placeholder structure to design ingestion pipeline for real plan/network data.

**Example:**
```
Plan ingestion pipeline:
- Expected fields: plan_id, plan_name, plan_type, monthly_premium, deductible, copay, etc.
- Validate against placeholder schema
- Replace placeholder chunks when real data arrives
```

**Why Safe:** Internal process, no customer exposure.

---

### ✅ Allowed Use Case 5: Mapping Cross-Reference

**Safe Use:** Mapping layer links FAQs to placeholder plan IDs, preparing for future real data.

**Example:**
```
MAP-005: FAQ-005 → RULE-003 → PLAN-003 (placeholder)
When answering FAQ-005: Use FAQ + RULE, add plan verification disclaimer
Future: When PLAN-003 replaced with real data, mapping still valid
```

**Why Safe:** Mapping doesn't claim placeholder content as fact, defers to verification.

---

## 6. What You MUST NEVER Do with Placeholders

### ❌ Forbidden Use Case 1: State Placeholder Data as Fact

**Unsafe Use:** Present placeholder plan benefits or provider details as confirmed truth.

**BAD Example:**
```
User: "What does the Basic Individual Plan cover?"
System: "The Basic Individual Plan covers outpatient visits, annual health screening, 
         emergency care, inpatient hospitalization, and prescription drugs, with a 
         deductible of AED 500 per year."
```

**Why Dangerous:** All benefit details in PLAN-001 are placeholders, not verified product specs.

**Consequence:** Legal liability, customer misinformation, regulatory violation.

---

### ❌ Forbidden Use Case 2: Confirm Provider Network Status

**Unsafe Use:** Tell customer a specific provider is in-network based on placeholder.

**BAD Example:**
```
User: "Is Dubai Medical Center in my network?"
System: "Yes, Dubai Medical Center is part of our Premium Network."
```

**Why Dangerous:** PROV-001 is a placeholder, not a verified provider contract.

**Consequence:** Customer schedules appointment at out-of-network provider, faces unexpected costs.

---

### ❌ Forbidden Use Case 3: Compare Placeholder Plans

**Unsafe Use:** Help customer choose between plans based on placeholder benefit details.

**BAD Example:**
```
User: "Should I choose Basic or Comprehensive Individual Plan?"
System: "The Comprehensive Individual Plan offers more coverage including 
         specialist visits and higher annual limits. It has a higher premium 
         but lower deductible than the Basic plan."
```

**Why Dangerous:** All plan comparison details are placeholders, not real product differences.

**Consequence:** Customer chooses plan based on incorrect information, disappointed when real benefits differ.

---

### ❌ Forbidden Use Case 4: Calculate Costs from Placeholder Data

**Unsafe Use:** Estimate out-of-pocket costs based on placeholder deductibles/copays.

**BAD Example:**
```
User: "How much will my visit cost?"
System: "With your Basic Individual Plan, you'll pay a AED 50 copay for the visit, 
         and your deductible is AED 500 per year."
```

**Why Dangerous:** Placeholder plan cost details are not real pricing.

**Consequence:** Customer budgets incorrectly, faces unexpected costs, files complaint.

---

### ❌ Forbidden Use Case 5: Display Placeholder Content Directly

**Unsafe Use:** Show placeholder plan details in a comparison table or provider search results.

**BAD Example:**
```
Plan Comparison Table:
┌────────────┬──────────┬────────────┬────────────┐
│ Plan       │ Premium  │ Deductible │ Coverage   │
├────────────┼──────────┼────────────┼────────────┤
│ Basic      │ AED 500  │ AED 500    │ Outpatient │
│ Compre...  │ AED 800  │ AED 300    │ Full       │
└────────────┴──────────┴────────────┴────────────┘
```

**Why Dangerous:** All details are placeholders, customer sees them as real options.

**Consequence:** Customer makes enrollment decisions based on fake data.

---

### ❌ Forbidden Use Case 6: Over-Weight Placeholders in Retrieval

**Unsafe Use:** Give placeholder chunks equal or higher retrieval weight than FAQ/Rules.

**BAD Example:**
```
retrieval_weight_hint:
  FAQ: 0.8
  Rules: 0.8
  Plans (Placeholder): 0.9  ← WRONG! Too high!
```

**Why Dangerous:** Placeholder content will dominate retrieval results.

**Consequence:** Customers receive placeholder data as top answers.

**Correct Weight:**
```
retrieval_weight_hint:
  FAQ: 1.0
  Rules: 0.9
  Plans (Placeholder): 0.2  ← Correct: Very low
```

---

## 7. Placeholder Detection and Prevention

### Pre-Deployment Checks

Before production, validate:

- [ ] **Filter Check:** Can filter `is_placeholder = true` chunks
- [ ] **Weight Check:** Placeholder retrieval_weight_hint ≤ 0.3
- [ ] **Safety Flag Check:** All placeholder chunks have `safe_for_client_direct_use = false`
- [ ] **Disclaimer Check:** Plan/network questions trigger verification disclaimers
- [ ] **Test Queries:** Run plan/network questions, verify no placeholder facts in answers

---

### Runtime Monitoring

Monitor for placeholder leaks:

1. **Content Scanning:** Scan generated answers for phrases from placeholder chunks
2. **Alert on Patterns:** Alert if answer contains "Basic Individual Plan covers" or "Dubai Medical Center is in-network"
3. **Manual Review:** Periodically review sample answers for placeholder content
4. **User Feedback:** Monitor customer complaints about incorrect plan/provider info

---

### Automated Guardrails

Implement code-level checks:

```python
def generate_answer(retrieved_chunks):
    # Check for placeholder content
    has_placeholder = any(chunk.get('is_placeholder') == True for chunk in retrieved_chunks)
    
    if has_placeholder:
        # Filter placeholder chunks OR add disclaimer
        if customer_facing:
            # Option 1: Remove placeholder chunks
            retrieved_chunks = [c for c in retrieved_chunks if not c.get('is_placeholder')]
            
            # Option 2: Add strong disclaimer
            if any(c.get('chunk_type') == 'Plans' for c in retrieved_chunks):
                disclaimer = "Specific plan details vary. Check your policy documents."
            if any(c.get('chunk_type') == 'Network' for c in retrieved_chunks):
                disclaimer = "Verify provider network status with customer service."
    
    # Generate answer from non-placeholder content only
    answer = generate(retrieved_chunks)
    return answer + disclaimer if has_placeholder else answer
```

---

## 8. Replacing Placeholders with Real Data

### When Real Data Arrives

**For Plans:**
1. Obtain approved product documentation (benefits, costs, exclusions, limitations)
2. Create new plan chunks with `is_placeholder: false`
3. Set `retrieval_weight_hint: 0.9` or higher
4. Set `safe_for_client_direct_use: true` (if content is customer-ready)
5. Mark old placeholder chunks as `status: "Deprecated"`
6. Update mapping references to new plan IDs
7. Remove deprecated placeholders from active retrieval within 30 days

**For Network:**
1. Obtain verified provider contract data (provider names, types, locations, network status)
2. Create new network chunks with `is_placeholder: false`
3. Set `retrieval_weight_hint: 0.8` or higher
4. Set `safe_for_client_direct_use: true` (if verified)
5. Mark old placeholder chunks as `status: "Deprecated"`
6. Update mapping references to new provider IDs
7. Remove deprecated placeholders from active retrieval within 30 days

---

### Migration Checklist

When replacing placeholders:

- [ ] **Verify New Data:** Confirm data is approved, accurate, verified
- [ ] **Create New Chunks:** Generate new chunks with correct flags (is_placeholder: false)
- [ ] **Update Mappings:** Revise mapping chunks to reference new IDs
- [ ] **Deprecate Old Chunks:** Mark placeholder chunks as "Deprecated"
- [ ] **Archive Placeholders:** Move deprecated chunks to archive (keep for audit trail)
- [ ] **Test Retrieval:** Verify new chunks retrieve correctly
- [ ] **Test Answers:** Verify answers now include real data, not placeholders
- [ ] **Monitor Quality:** Track answer quality improvement post-migration

---

### Placeholder Sunset Policy

**Timeline:**
- **Plans:** Replace within 6 months of policy finalization
- **Network:** Replace within 3 months of provider partnership agreements

**If Real Data Delayed:**
- Continue filtering placeholders from customer-facing retrieval
- Continue adding verification disclaimers
- Consider creating "Coming Soon" messaging for unavailable details
- Escalate to business leadership if delay impacts customer experience

---

## 9. Disclaimer Requirements for Placeholder Context

When placeholder content influences an answer (even indirectly):

### Plan-Related Disclaimers

**Tier 1 (Minimal Placeholder Influence):**
```
"Specific plan details vary. Please check your policy documents."
```

**Tier 2 (Moderate Placeholder Influence):**
```
"Plan benefits and coverage details depend on your specific policy. 
 Please refer to your policy documents for your exact plan benefits, 
 exclusions, and limitations."
```

**Tier 3 (Heavy Placeholder Influence - Avoid if Possible):**
```
"The information provided here is general guidance only and does not 
 represent your specific plan benefits. Please contact customer service 
 or review your policy documents for accurate coverage information."
```

---

### Network-Related Disclaimers

**Tier 1 (Minimal Placeholder Influence):**
```
"Verify provider network status with customer service."
```

**Tier 2 (Moderate Placeholder Influence):**
```
"Provider network status can change. Please verify that [provider name] 
 is currently in-network by checking our online provider directory or 
 contacting customer service."
```

**Tier 3 (Heavy Placeholder Influence - Avoid if Possible):**
```
"Provider information provided here is for reference only and may not 
 reflect current network status. Always verify provider participation 
 before scheduling appointments by checking our online provider directory 
 or contacting customer service."
```

---

## 10. Training and Communication

### For RAG System Developers

**Key Messages:**
- Placeholders are structural only, never confirmation
- Always filter or disclaim placeholder content
- Test rigorously for placeholder leaks
- Monitor production for violations

---

### For Customer Service Teams

**Key Messages:**
- Do not rely on placeholder plan/network data
- Always verify plan benefits with policy documents
- Always verify provider status with provider directory
- Escalate if customers report incorrect plan/provider info from chatbot

---

### For Product/Business Teams

**Key Messages:**
- Placeholders are temporary scaffolding, not products
- Real plan/network data urgently needed to improve customer experience
- Current system limited to general guidance until real data integrated
- Timeline for placeholder replacement: Plans (6 months), Network (3 months)

---

## 11. Compliance and Auditing

### Regular Audits

**Quarterly Review:**
- Sample 100 customer interactions
- Check for placeholder content in answers
- Verify disclaimer compliance
- Report violations to Risk & Compliance

**Annual Review:**
- Comprehensive audit of all placeholder chunks
- Assess progress on real data integration
- Update policy if needed
- Certify compliance with regulatory requirements

---

### Incident Reporting

**If Placeholder Leak Detected:**
1. **Immediate:** Remove affected answer from production
2. **Document:** Log incident details (what was said, to whom, when)
3. **Investigate:** Determine root cause (missing filter, code bug, etc.)
4. **Fix:** Update guardrails to prevent recurrence
5. **Report:** Notify Risk & Compliance within 24 hours
6. **Remediate:** Contact affected customers if needed (depends on severity)

---

## 12. Policy Enforcement

### Mandatory Requirements

These rules are **NON-NEGOTIABLE**:

1. ✅ All placeholder chunks MUST have `is_placeholder: true`
2. ✅ All placeholder chunks MUST have `safe_for_client_direct_use: false`
3. ✅ All placeholder chunks MUST have `retrieval_weight_hint ≤ 0.3`
4. ✅ Customer-facing retrieval MUST filter placeholder chunks OR add disclaimers
5. ✅ Answers MUST NOT state placeholder data as confirmed facts
6. ✅ Pre-deployment testing MUST verify placeholder handling

**Violation Consequences:**
- Production deployment BLOCKED until compliance verified
- Incident investigation if leak occurs in production
- Potential system rollback if high-risk violation detected

---

## 13. Summary: Placeholder Golden Rules

### ✅ DO:
- Use placeholders for routing and context awareness
- Filter placeholders from customer-facing retrieval
- Add verification disclaimers when plans/network are relevant
- Replace placeholders with real data as soon as available
- Monitor for placeholder leaks
- Test rigorously

### ❌ DO NOT:
- State placeholder data as confirmed facts
- Confirm provider network status from placeholders
- Compare plans based on placeholder benefits
- Calculate costs from placeholder data
- Over-weight placeholders in retrieval
- Deploy without placeholder guardrails

---

## 14. Critical Reminder

🚨 **Placeholder chunks exist to prepare for future real data, NOT to provide customer answers.** 🚨

**If you're unsure whether content is placeholder:**
1. Check `is_placeholder` field
2. Check `status` field (Pending Detail = likely placeholder)
3. Check `safe_for_client_direct_use` field
4. **When in doubt, add a disclaimer**

**If placeholder content appears in a customer answer:**
1. This is a policy violation
2. Remove the answer immediately
3. Report the incident
4. Fix the root cause

---

**End of Placeholder Handling Policy**

✅ **Enforcement Level:** MANDATORY  
⚠️ **Violation Risk:** Legal liability, customer misinformation, regulatory penalties  
📅 **Review Cycle:** Quarterly, or when real data becomes available
