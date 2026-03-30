# Future Ingestion Checklist - Micro Insurance KB V1

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Practical checklist for future knowledge base ingestion and updates  
**Audience:** Knowledge engineers, data engineers, RAG system maintainers

---

## 1. Overview

This checklist guides future ingestion of:
- New FAQ content
- New business rules
- **Real plan data** (replaces placeholders)
- **Real provider/network data** (replaces placeholders)
- Updated mapping references
- Content revisions and corrections

Use this checklist to ensure data quality, compliance, and retrieval safety when adding or updating knowledge.

---

## 2. Before Adding New FAQ Content

### Pre-Ingestion Checks

- [ ] **Source Verification:** FAQ content sourced from approved documentation or training materials
- [ ] **Q&A Completeness:** Question, internal answer, and client answer all populated
- [ ] **Duplicate Check:** Question doesn't already exist in knowledge base
- [ ] **Category Assignment:** FAQ assigned to appropriate category and subcategory
- [ ] **Status Setting:** Status correctly set (Approved, Needs Review, Pending Detail)
- [ ] **Priority Level:** Business priority assigned (High, Medium, Low)
- [ ] **Dependency Flags:** `needs_plan_link`, `needs_rule_link`, `needs_network_check` set accurately
- [ ] **Client-Facing Readiness:** Client answer appropriate for customer viewing (no jargon, no internal notes)

### Content Quality Checks

- [ ] **Accuracy:** Answer is factually correct
- [ ] **Clarity:** Answer is clear and understandable to non-experts
- [ ] **Completeness:** Answer addresses the question fully (or acknowledges gap)
- [ ] **Tone:** Answer is professional, empathetic, helpful
- [ ] **Compliance:** Answer doesn't make unverified claims or guarantees
- [ ] **Generality:** Answer is generic enough to apply broadly (not overly specific without verification)

### Metadata Assignment

- [ ] **chunk_id:** Assigned unique ID (e.g., FAQ-CHUNK-095)
- [ ] **source_id:** Assigned source FAQ ID (e.g., FAQ-095)
- [ ] **status:** Set to "Needs Review" initially (promote to "Approved" after review)
- [ ] **is_placeholder:** Set to `false` (FAQs are not placeholders)
- [ ] **safe_for_client_direct_use:** Set to `true` if content is customer-ready
- [ ] **retrieval_weight_hint:** Set to 0.95 for "Needs Review", 1.0 after "Approved"
- [ ] **requires_plan_confirmation:** Set to `true` if answer depends on plan-specific truth
- [ ] **requires_network_verification:** Set to `true` if answer depends on provider/network truth

### Ingestion Steps

1. **Create TSV/Excel Source:** Add FAQ row to source data file
2. **Convert to JSONL:** Run conversion script to generate new chunk
3. **Validate JSON:** Verify chunk is valid JSON with all required fields
4. **Test Retrieval:** Query should retrieve new FAQ appropriately
5. **Create Mapping:** Link FAQ to related rules if applicable
6. **Set Status:** Mark as "Needs Review" until final approval
7. **Monitor Performance:** Track how often FAQ is retrieved and user feedback

---

## 3. Before Adding New Rules Content

### Pre-Ingestion Checks

- [ ] **Source Verification:** Rule sourced from policy documents, legal guidance, or business requirements
- [ ] **Rule Uniqueness:** Rule doesn't duplicate existing rules
- [ ] **Category Assignment:** Rule assigned to appropriate category
- [ ] **Applicability:** Rule is generic enough to apply across use cases (not overly plan-specific)
- [ ] **Clear Description:** Rule description is detailed and unambiguous
- [ ] **Client-Safe Summary:** Client-facing summary is accurate and appropriate for customers
- [ ] **Internal Usage Note:** Internal note clarifies when/how to apply rule
- [ ] **Status Setting:** Status set to "Needs Review" initially (promote to "Active" after approval)

### Content Quality Checks

- [ ] **Accuracy:** Rule reflects current policy or business logic
- [ ] **Clarity:** Rule is clearly written and easy to understand
- [ ] **Completeness:** Rule covers all relevant scenarios or exceptions
- [ ] **Compliance:** Rule aligns with legal/regulatory requirements
- [ ] **No Contradictions:** Rule doesn't contradict other existing rules

### Metadata Assignment

- [ ] **chunk_id:** Assigned unique ID (e.g., RULE-CHUNK-045)
- [ ] **source_id:** Assigned source Rule ID (e.g., RULE-045)
- [ ] **status:** Set to "Needs Review" initially
- [ ] **is_placeholder:** Set to `false`
- [ ] **safe_for_client_direct_use:** Set to `true` if client_safe_summary is customer-ready
- [ ] **retrieval_weight_hint:** Set to 0.85 for "Needs Review", 0.9 after "Active"

### Ingestion Steps

1. **Create Source Data:** Add rule to source data file
2. **Convert to JSONL:** Generate chunk
3. **Validate JSON:** Check all required fields present
4. **Test Retrieval:** Verify rule retrieves correctly for relevant queries
5. **Link to FAQs:** Create or update mapping to link rule to relevant FAQs
6. **Set Status:** Mark as "Needs Review" until approved
7. **Monitor Usage:** Track how rule is used in answer generation

---

## 4. Before Adding Real Plan Data (Replacing Placeholders)

### 🚨 CRITICAL: Placeholder Replacement

This is a **HIGH-PRIORITY** task. Replacing placeholder plans with real data significantly improves system safety and answer quality.

### Pre-Ingestion Requirements

- [ ] **Approved Product Documentation:** Have official, legal-reviewed plan documents
- [ ] **Benefit Details:** All benefit categories defined (outpatient, inpatient, dental, vision, etc.)
- [ ] **Cost Details:** Premiums, deductibles, copays, out-of-pocket maximums confirmed
- [ ] **Exclusions/Limitations:** Plan exclusions and limitations documented
- [ ] **Effective Dates:** Plan effective dates and validity periods confirmed
- [ ] **Compliance Review:** Legal/compliance team has approved plan details for customer communication
- [ ] **Naming Consistency:** Plan names match official marketing materials

### Data Quality Checks

- [ ] **Accuracy:** All benefit and cost details are accurate and current
- [ ] **Completeness:** All required fields populated (no "TBD" or placeholders)
- [ ] **Currency:** Data reflects current plan offerings (not outdated)
- [ ] **Verification:** Data cross-checked against authoritative source (policy docs, admin system)

### Metadata Assignment (Real Plan)

- [ ] **chunk_id:** New unique ID (e.g., PLAN-CHUNK-101) or reuse placeholder ID if replacing directly
- [ ] **source_id:** New plan ID (e.g., PLAN-101) or replace placeholder ID
- [ ] **status:** Set to "Approved" (only ingest approved product data)
- [ ] **is_placeholder:** Set to `false` ⚠️ CRITICAL
- [ ] **safe_for_client_direct_use:** Set to `true` if plan details can be shared directly with customers
- [ ] **retrieval_weight_hint:** Set to 0.9 (high - real plan data)
- [ ] **requires_plan_confirmation:** Set to `false` if this IS the confirmed plan data, or `true` if still requires user to check their specific policy
- [ ] **plan_name, plan_type, benefit fields:** All populated with real data

### Placeholder Deprecation Steps

1. **Mark Old Placeholder as Deprecated:**
   - Update placeholder chunk: `status: "Deprecated"`
   - Add `deprecated_date: "[current date]"`
   - Add `superseded_by: "PLAN-101"` (new plan chunk ID)

2. **Remove Placeholder from Active Retrieval:**
   - Filter out deprecated chunks (exclude `status = "Deprecated"`)
   - Or set `retrieval_weight_hint: 0.0` to zero out

3. **Update Mappings:**
   - Find all mapping chunks referencing old placeholder plan ID
   - Update `related_plan_id` to new real plan ID
   - Update mapping status if needed (e.g., "Needs Review" → "Approved")

4. **Archive Placeholder:**
   - Move deprecated placeholder chunk to archive collection
   - Keep for audit trail (don't delete)

### Ingestion Steps (Real Plan)

1. **Create Real Plan Chunk:** Build new chunk with verified data, `is_placeholder: false`
2. **Validate:** Check all required fields, ensure `is_placeholder: false`
3. **Ingest:** Add to vector store or search index
4. **Test Retrieval:** Query for plan details, verify real plan retrieved (not placeholder)
5. **Test Answers:** Verify answers now include real plan details without over-caution disclaimers
6. **Deprecate Placeholder:** Mark old placeholder as deprecated, update mappings
7. **Archive Placeholder:** Move to archive within 30 days
8. **Monitor Quality:** Track answer quality improvement, user feedback

### Quality Validation (Post-Ingestion)

- [ ] **Placeholder Filter Test:** Query for `is_placeholder: true`, verify old placeholder not in active results
- [ ] **Real Data Retrieval Test:** Query "What does [plan name] cover?", verify real data retrieved
- [ ] **Disclaimer Test:** Verify answers no longer over-disclaim when real plan data is used
- [ ] **Mapping Link Test:** Verify FAQs linked to plans now retrieve real plan details
- [ ] **Cross-Reference Test:** All mapping references resolve to real plan IDs (not deprecated placeholders)

---

## 5. Before Adding Real Provider/Network Data (Replacing Placeholders)

### 🚨 CRITICAL: Placeholder Replacement

This is a **HIGH-PRIORITY** task. Replacing placeholder network with real data enables provider verification and improves customer trust.

### Pre-Ingestion Requirements

- [ ] **Verified Provider Contracts:** Have signed contracts or verified agreements with providers
- [ ] **Provider Details:** Name, type, location, contact info confirmed
- [ ] **Network Assignment:** Know which network(s) each provider belongs to
- [ ] **In-Network Status:** Verify provider is currently active and in-network
- [ ] **Specialty/Services:** Provider specialties and services documented
- [ ] **Verification Method:** Confirm how customers should verify provider status (online directory, customer service)
- [ ] **Effective Dates:** Provider network participation effective dates confirmed

### Data Quality Checks

- [ ] **Accuracy:** Provider details match official records
- [ ] **Currency:** Provider is currently participating in network (not outdated)
- [ ] **Completeness:** All required fields populated
- [ ] **Contact Info:** Provider contact information accurate and current
- [ ] **Network Accuracy:** Network assignments correct and current

### Metadata Assignment (Real Provider)

- [ ] **chunk_id:** New unique ID (e.g., NETWORK-CHUNK-101) or reuse placeholder ID
- [ ] **source_id:** New provider ID (e.g., PROV-101) or replace placeholder ID
- [ ] **status:** Set to "Approved" (only ingest verified provider data)
- [ ] **is_placeholder:** Set to `false` ⚠️ CRITICAL
- [ ] **safe_for_client_direct_use:** Set to `true` if provider details can be shared with customers
- [ ] **retrieval_weight_hint:** Set to 0.8 (high - real provider data)
- [ ] **requires_network_verification:** Set to `true` (always recommend verification even for real data, as network status can change)
- [ ] **provider_name, provider_type, network_name, location fields:** All populated with real data

### Placeholder Deprecation Steps

1. **Mark Old Placeholder as Deprecated:**
   - Update placeholder chunk: `status: "Deprecated"`
   - Add `deprecated_date: "[current date]"`
   - Add `superseded_by: "PROV-101"` (new provider chunk ID)

2. **Remove Placeholder from Active Retrieval:**
   - Filter out deprecated chunks
   - Or set `retrieval_weight_hint: 0.0`

3. **Update Mappings:**
   - Find all mapping chunks referencing old placeholder provider ID
   - Update provider references to new real provider ID

4. **Archive Placeholder:**
   - Move deprecated chunk to archive
   - Keep for audit trail

### Ingestion Steps (Real Provider)

1. **Create Real Provider Chunk:** Build new chunk with verified data, `is_placeholder: false`
2. **Validate:** Check all required fields, ensure `is_placeholder: false`
3. **Ingest:** Add to vector store or search index
4. **Test Retrieval:** Query for provider, verify real provider retrieved (not placeholder)
5. **Test Answers:** Verify answers acknowledge real provider availability (with verification disclaimer)
6. **Deprecate Placeholder:** Mark old placeholder as deprecated
7. **Archive Placeholder:** Move to archive within 30 days
8. **Monitor Quality:** Track answer quality, provider verification requests

### Quality Validation (Post-Ingestion)

- [ ] **Placeholder Filter Test:** Verify old placeholder not in active results
- [ ] **Real Data Retrieval Test:** Query "Is [provider name] in-network?", verify real data retrieved
- [ ] **Verification Disclaimer Test:** Verify answers still recommend verifying provider status (network can change)
- [ ] **Mapping Link Test:** Verify network-related FAQs now retrieve real provider data
- [ ] **Cross-Reference Test:** All mapping references resolve to real provider IDs

---

## 6. Before Adding or Updating Mappings

### Pre-Ingestion Checks

- [ ] **Question-Rule Relationship:** Verify rule is genuinely relevant to FAQ
- [ ] **Confidence Level:** Assign appropriate confidence (High, Medium, Low)
- [ ] **Primary/Secondary/Tertiary:** Identify most relevant rule as primary
- [ ] **Plan/Network References:** If linking to plan or provider, verify ID exists
- [ ] **Answer Type:** Classify answer complexity (Direct, Multi-Part, Requires Document, Requires Agent)
- [ ] **Dependency Flags:** Set needs_plan_link, needs_rule_link, needs_network_check appropriately

### Content Quality Checks

- [ ] **Relevance:** Rule actually helps answer the FAQ (not tangentially related)
- [ ] **Completeness:** All relevant rules linked (didn't miss important rules)
- [ ] **No Redundancy:** No duplicate mappings for same FAQ-Rule pair

### Metadata Assignment

- [ ] **chunk_id:** Assigned unique mapping ID (e.g., MAP-CHUNK-045)
- [ ] **source_id:** Assigned mapping ID (e.g., MAP-045)
- [ ] **question_id, primary_rule_id:** Required fields populated
- [ ] **confidence:** Set based on relevance strength
- [ ] **status:** Set based on review state
- [ ] **retrieval_weight_hint:** Set based on confidence (High=0.6, Medium=0.5, Low=0.4)

### Ingestion Steps

1. **Create Mapping:** Define FAQ-to-rule relationships
2. **Validate:** Ensure referenced IDs exist (no broken links)
3. **Test Retrieval:** Verify FAQ retrieval now enriched with linked rules
4. **Test Answers:** Verify answers benefit from cross-reference context
5. **Monitor Quality:** Track whether mapping improves answer quality

---

## 7. When to Re-Embed or Re-Index

### Trigger 1: Major Content Changes

**Re-embed if:**
- FAQ or Rule text significantly changed
- New FAQ or Rule added
- Real plan/network data replaces placeholder

**Why:** Embedding vectors must match current text content.

**Process:**
1. Generate new embeddings for changed chunks
2. Update vector store with new embeddings
3. Test retrieval to ensure updated content ranks correctly

---

### Trigger 2: Metadata Changes Only

**No re-embedding needed if:**
- Status changed (e.g., "Needs Review" → "Approved")
- Retrieval weight hint adjusted
- Other metadata fields updated

**Why:** Metadata doesn't affect embedding vectors.

**Process:**
1. Update metadata in search index or vector store metadata layer
2. No embedding regeneration required
3. Test filtering/weighting to ensure metadata changes applied

---

### Trigger 3: Placeholder Replacement

**Re-embed required:**
- Old placeholder chunk marked deprecated
- New real plan/network chunk created with different text

**Why:** Real data has different content than placeholder.

**Process:**
1. Generate embedding for new real chunk
2. Ingest new chunk
3. Deprecate old placeholder (or set weight to 0)
4. Test retrieval to ensure real chunk ranks higher

---

### Trigger 4: Ingestion of New Chunks

**Re-embed required:**
- New FAQ, Rule, Plan, or Network chunk added

**Why:** Can't retrieve new content without its embedding.

**Process:**
1. Generate embedding for new chunk
2. Add to vector store
3. Test retrieval for new content

---

### Trigger 5: Bulk Changes

**Consider full re-embedding if:**
- 20%+ of knowledge base changed
- Switching to new embedding model
- Major schema changes

**Why:** Ensures all embeddings consistent and up-to-date.

**Process:**
1. Backup current vector store
2. Regenerate all embeddings
3. Rebuild vector store
4. Comprehensive testing across all queries

---

## 8. Validation Checklist (Post-Ingestion)

After any ingestion, validate:

- [ ] **Chunk Count:** Expected number of chunks ingested (no missing chunks)
- [ ] **Required Fields:** All chunks have required fields populated
- [ ] **ID Uniqueness:** No duplicate chunk_id values
- [ ] **Cross-References:** All referenced IDs resolve (no broken links)
- [ ] **Placeholder Flags:** Plans/network placeholders marked correctly (or deprecated if replaced)
- [ ] **Status Values:** Valid status enums used
- [ ] **Retrieval Test:** Sample queries return expected chunks
- [ ] **Guardrail Test:** Placeholder content filtered or disclaimed
- [ ] **Answer Quality Test:** Generated answers improved (if content updated)
- [ ] **Metadata Indexed:** Can filter by status, category, confidence, etc.

---

## 9. Deprecation Checklist

When deprecating old content:

- [ ] **Update Status:** Set `status: "Deprecated"`
- [ ] **Add Deprecated Date:** Set `deprecated_date: "YYYY-MM-DD"`
- [ ] **Link to Replacement:** Set `superseded_by: "NEW-CHUNK-ID"` if applicable
- [ ] **Remove from Active Retrieval:** Filter out or set weight to 0
- [ ] **Update Cross-References:** Revise mapping chunks to reference new IDs
- [ ] **Archive (Optional):** Move to archive collection for audit trail
- [ ] **Test Retrieval:** Verify deprecated chunks not in active results
- [ ] **Monitor:** Ensure no systems still referencing deprecated content

---

## 10. Quality Control Checklist

### Pre-Deployment

- [ ] **Schema Validation:** All chunks match expected schema
- [ ] **Required Fields:** No missing required fields
- [ ] **Format Validation:** JSONL format correct (one JSON per line)
- [ ] **Encoding:** UTF-8 encoding, no corruption
- [ ] **ID Validation:** All IDs unique and follow format conventions
- [ ] **Link Validation:** Cross-references resolve
- [ ] **Placeholder Flagging:** Plans/network placeholders marked correctly
- [ ] **Weight Assignment:** Retrieval hints appropriate

### Post-Deployment

- [ ] **Retrieval Testing:** Sample queries retrieve expected chunks
- [ ] **Answer Quality Testing:** Answers improved or maintained quality
- [ ] **Guardrail Testing:** Placeholder content filtered/disclaimed correctly
- [ ] **Cross-Reference Testing:** Mappings enrich context as expected
- [ ] **Status Filtering:** Can filter by Approved/Active for production
- [ ] **Performance Testing:** Retrieval latency acceptable
- [ ] **Monitor Logs:** Check for errors or warnings in ingestion logs

---

## 11. Rollback Plan

### If Ingestion Causes Issues

**Immediate Actions:**
1. **Identify Issue:** What's broken? (retrieval accuracy, answer quality, errors, etc.)
2. **Assess Impact:** How many users affected? Severity?
3. **Decide:** Rollback or quick fix?

**Rollback Steps:**
1. **Restore Previous Vector Store:** Use backup from before ingestion
2. **Restore Previous Metadata:** Revert metadata changes
3. **Test:** Verify issue resolved
4. **Investigate:** Determine root cause off-line
5. **Fix:** Correct issue in staging environment
6. **Re-Ingest:** Try again with corrected data

**Prevention:**
- Always backup vector store before major ingestion
- Test in staging environment first
- Gradual rollout (canary deployment) for large changes

---

## 12. Ongoing Maintenance Checklist

### Weekly

- [ ] **Monitor Retrieval Quality:** Review metrics (relevance, user feedback)
- [ ] **Check for Errors:** Review system logs for ingestion errors or warnings
- [ ] **Track Placeholder Leaks:** Alert if placeholder content in customer answers

### Monthly

- [ ] **Content Audit:** Sample review of answers for accuracy
- [ ] **Metadata Accuracy:** Verify status, confidence, flags still accurate
- [ ] **Broken Link Check:** Verify cross-references still resolve
- [ ] **Performance Review:** Check retrieval latency, system health

### Quarterly

- [ ] **Comprehensive Audit:** Review all content for accuracy, currency, completeness
- [ ] **Placeholder Progress:** Assess progress on replacing placeholders with real data
- [ ] **Policy Review:** Update INGESTION_POLICY.md if needed
- [ ] **Guardrail Validation:** Test all guardrails still effective
- [ ] **User Feedback Analysis:** Review user feedback, identify content gaps

### Annually

- [ ] **Full KB Review:** Comprehensive review of entire knowledge base
- [ ] **Compliance Certification:** Certify compliance with policies and regulations
- [ ] **Technology Refresh:** Assess whether to upgrade embedding models, vector stores, etc.
- [ ] **Strategic Planning:** Plan next year's KB expansion and improvement

---

## 13. Contact and Escalation

### For Urgent Issues

**If ingestion fails or causes production issues:**
- Escalate to: Knowledge Engineering Lead
- Backup contact: RAG System Lead
- After hours: On-call engineer (see incident response plan)

### For Policy Questions

**If unsure about ingestion policy:**
- Refer to: INGESTION_POLICY.md, PLACEHOLDER_HANDLING_POLICY.md
- Contact: Knowledge Engineering Team
- Compliance questions: Risk & Compliance Team

### For Data Quality Issues

**If source data quality questionable:**
- Contact: Data Quality Team, Business Analysts
- Verify with: Legal/Compliance (for plan/policy content)

---

## 14. Key Reminders

### Critical Rules

1. ✅ **Always verify source data** before ingestion
2. ✅ **Always set is_placeholder flag correctly** (false for real data, true for placeholders)
3. ✅ **Always mark placeholder chunks as deprecated** when replacing with real data
4. ✅ **Always test retrieval after ingestion** before production deployment
5. ✅ **Always backup vector store** before major changes

### Common Mistakes to Avoid

- ❌ Ingesting placeholder data without `is_placeholder: true` flag
- ❌ Forgetting to update mappings when replacing placeholders
- ❌ Not re-embedding after content changes
- ❌ Skipping validation after ingestion
- ❌ Not testing guardrails after adding plan/network content
- ❌ Deploying to production without staging environment testing

---

## 15. Quick Reference: Ingestion Decision Tree

```
What are you ingesting?
├─ New FAQ
│  ├─ Approved? → Set status="Approved", weight=1.0
│  ├─ Needs Review? → Set status="Needs Review", weight=0.95
│  └─ Pending Detail? → Set status="Pending Detail", weight=0.9
│
├─ New Rule
│  ├─ Approved? → Set status="Active", weight=0.9
│  └─ Needs Review? → Set status="Needs Review", weight=0.85
│
├─ Real Plan Data (Replacing Placeholder)
│  ├─ Set is_placeholder=false, weight=0.9
│  ├─ Deprecate old placeholder
│  └─ Update mappings
│
├─ Real Provider Data (Replacing Placeholder)
│  ├─ Set is_placeholder=false, weight=0.8
│  ├─ Deprecate old placeholder
│  └─ Update mappings
│
└─ New Mapping
   ├─ High Confidence? → weight=0.6
   ├─ Medium Confidence? → weight=0.5
   └─ Low Confidence? → weight=0.4
```

---

**End of Future Ingestion Checklist**

✅ **Use this checklist for every ingestion to ensure quality and compliance**  
⚠️ **Special attention required when replacing placeholder plans/network with real data**  
📋 **Keep this checklist updated as policies and processes evolve**
