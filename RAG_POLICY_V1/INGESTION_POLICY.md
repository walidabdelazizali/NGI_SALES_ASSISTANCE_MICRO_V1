# RAG Ingestion Policy - Micro Insurance KB V1

**Version:** 1.0  
**Date:** March 19, 2026  
**Package:** KB_PACK_V1  
**Status:** Policy Approved - Implementation Pending

---

## 1. Executive Summary

This policy defines **what**, **when**, and **how** to ingest knowledge chunks from the Micro Insurance KB V1 package into a RAG (Retrieval-Augmented Generation) system. The policy establishes clear ingestion phases, priority levels, and safety guardrails to ensure:

1. **Strong knowledge** (FAQs, Rules) is prioritized and treated as high-confidence
2. **Placeholder knowledge** (Plans, Network) is ingested with explicit caution flags
3. **Reference knowledge** (Mapping) supports cross-linking and routing
4. **Future retrieval systems cannot misrepresent incomplete data as confirmed facts**

---

## 2. Package Inventory

### Source Location
**C:\micro-insurance-kb-v1\KB_PACK_V1**

### Available Chunk Files

| File | Chunks | Type | Content Strength | Ingestion Priority |
|------|--------|------|------------------|-------------------|
| `faq_chunks.jsonl` | 20 | FAQ | **HIGH** - Approved/Review | **Phase 1** |
| `rules_chunks.jsonl` | 27 | Rules | **HIGH** - Active/Review | **Phase 1** |
| `mapping_reference.jsonl` | 20 | Mapping | **MEDIUM** - Cross-reference | **Phase 1** |
| `plans_chunks.jsonl` | 10 | Plans | **LOW** - Placeholder Only | **Phase 2** |
| `network_chunks.jsonl` | 10 | Network | **LOW** - Placeholder Only | **Phase 2** |

**Total Chunks:** 87

---

## 3. Ingestion Phase Design

### Phase 1: Strong Knowledge Foundation (PRIORITY)

**Objective:** Establish reliable, high-confidence knowledge base for customer-facing Q&A and business logic reasoning.

**Files to Ingest:**
1. ✅ `faq_chunks.jsonl` (20 chunks)
   - **Why First:** Direct customer questions and approved answers
   - **Confidence:** High (9 Approved, 7 Needs Review, 4 Pending Detail)
   - **Use Case:** Primary retrieval for customer inquiries
   - **Risk:** Low - content is training-derived and hardened

2. ✅ `rules_chunks.jsonl` (27 chunks)
   - **Why First:** Business logic and policy reasoning layer
   - **Confidence:** High (26 Active, 1 Needs Review)
   - **Use Case:** Support FAQ answers with detailed reasoning
   - **Risk:** Low - generic rules apply across insurance domain

3. ✅ `mapping_reference.jsonl` (20 chunks)
   - **Why First:** Links FAQs to related rules, plans, network
   - **Confidence:** Medium (9 Approved, 7 Needs Review, 4 Pending Detail)
   - **Use Case:** Cross-reference navigation, context enrichment
   - **Risk:** Medium - 3 mappings have low confidence, some provisional

**Phase 1 Outcome:**
- **67 chunks ingested** (77% of package)
- **Retrieval system can answer common questions confidently**
- **Business rules support reasoning and explanations**
- **Cross-references enable multi-hop retrieval**

---

### Phase 2: Placeholder Knowledge (CAUTION REQUIRED)

**Objective:** Add structural plan and network data for context and routing, but **NEVER** present as confirmed benefits or live provider facts.

**Files to Ingest:**
4. ⚠️ `plans_chunks.jsonl` (10 chunks)
   - **Why Last:** All chunks are placeholders (status: "Pending Detail")
   - **Confidence:** Very Low - structural scaffolding only
   - **Use Case:** Plan type awareness, future data preparation
   - **Risk:** **HIGH** - easily misinterpreted as real benefits
   - **Required Flags:** `is_placeholder: true`, `requires_plan_confirmation: true`

5. ⚠️ `network_chunks.jsonl` (10 chunks)
   - **Why Last:** All chunks are placeholders (status: "Pending Detail")
   - **Confidence:** Very Low - structural scaffolding only
   - **Use Case:** Provider type awareness, future data preparation
   - **Risk:** **HIGH** - easily misinterpreted as live provider directory
   - **Required Flags:** `is_placeholder: true`, `requires_network_verification: true`

**Phase 2 Outcome:**
- **20 additional chunks ingested** (23% of package, 100% total)
- **Plan and provider awareness available for routing**
- **Retrieval system MUST apply strict guardrails**
- **Answers MUST include verification disclaimers**

---

## 4. Ingestion Priority Matrix

### Recommended Order

```
Priority 1 (Immediate):
├── faq_chunks.jsonl ────────────► High confidence, customer-facing
├── rules_chunks.jsonl ─────────► High confidence, reasoning layer
└── mapping_reference.jsonl ───► Medium confidence, cross-reference

Priority 2 (With Guardrails):
├── plans_chunks.jsonl ─────────► Low confidence, PLACEHOLDER ONLY
└── network_chunks.jsonl ───────► Low confidence, PLACEHOLDER ONLY
```

### Searchability Levels

| Chunk Type | Direct Search | Context Search | Reference Only | Weight Hint |
|------------|---------------|----------------|----------------|-------------|
| FAQ | ✅ Yes | ✅ Yes | No | 1.0 (High) |
| Rules | ✅ Yes | ✅ Yes | No | 0.9 (High) |
| Mapping | Limited | ✅ Yes | ✅ Yes | 0.5 (Medium) |
| Plans | **No** | Limited | ✅ Yes | 0.2 (Very Low) |
| Network | **No** | Limited | ✅ Yes | 0.2 (Very Low) |

**Definitions:**
- **Direct Search:** Chunk appears in primary retrieval results for user queries
- **Context Search:** Chunk retrieved as supporting context after primary results
- **Reference Only:** Chunk used for internal linking, not shown to users
- **Weight Hint:** Suggested retrieval scoring multiplier (1.0 = full weight)

---

## 5. Known Risks and Mitigations

### Risk 1: Placeholder Content Misrepresentation

**Risk:** Plans and network placeholders could be presented as confirmed insurance facts.

**Impact:** HIGH - Legal liability, customer misinformation, regulatory issues

**Mitigation:**
- ✅ All placeholder chunks flagged with `is_placeholder: true`
- ✅ Retrieval weight set to 0.2 (very low)
- ✅ Answers must include verification disclaimer
- ✅ Filter placeholder chunks for production customer-facing retrieval
- ✅ Use placeholder chunks for routing/interpretation only, not final answers

**Example Safe Use:**
```
User: "Does my plan cover dental?"
System retrieves FAQ-005, RULE-003, MAP-005, PLAN-003 (placeholder)
System responds: "Coverage depends on your specific plan type. 
               Please check your policy documents or contact customer service."
```

**Example Unsafe Use (NEVER DO THIS):**
```
System responds: "The Basic Individual Plan covers annual dental checkups."
(This is from PLAN-003 placeholder - NOT confirmed product data!)
```

---

### Risk 2: Low-Confidence Mappings

**Risk:** 3 mappings (MAP-012, MAP-013, MAP-017) have low confidence and provisional operational links.

**Impact:** Medium - May retrieve less relevant rules for operational questions

**Mitigation:**
- ✅ Confidence field exposed in metadata
- ✅ Monitor retrieval quality for these FAQs
- ✅ Add disclaimers for operational questions
- ✅ Refine mappings when dedicated operational rules exist

**Affected FAQs:**
- FAQ-011: I can't login to my member account
- FAQ-013: How do I access my insurance card?
- FAQ-017: How do I contact support?

---

### Risk 3: Incomplete FAQ Content

**Risk:** 4 FAQs marked "Pending Detail" lack operational specifics (refill process, card delivery, support channels).

**Impact:** Low - Generic answers may lack procedural detail

**Mitigation:**
- ✅ Status field preserved in metadata
- ✅ Answers should acknowledge when details are not yet defined
- ✅ Direct users to customer service for specific procedures
- ✅ Update FAQs when operational data becomes available

**Affected FAQs:**
- FAQ-011: How do I refill my prescriptions?
- FAQ-013: How do I access my insurance card?
- FAQ-017: How do I contact support?
- FAQ-020: Can I change my doctor or hospital?

---

## 6. Metadata Requirements for Ingestion

### Mandatory Fields (All Chunks)

Every ingested chunk MUST include:
- `chunk_id` - Unique identifier (e.g., FAQ-CHUNK-001)
- `chunk_type` - Type (FAQ, Rules, Plans, Network, Mapping)
- `source_file` - Origin file name
- `source_id` - Source document ID (e.g., FAQ-001, RULE-001)
- `status` - Content status (Approved, Needs Review, Pending Detail, Active)
- `text` - Retrieval-ready text content

### Critical Safety Fields

Chunks MUST include these safety flags:
- `is_placeholder` - Boolean flag (true for plans/network placeholders)
- `retrieval_weight_hint` - Suggested scoring multiplier (0.0-1.0)
- `safe_for_client_direct_use` - Boolean (false for placeholders)

### Optional but Recommended

- `confidence` - Mapping confidence (High, Medium, Low)
- `category` - Content category (for FAQ, Rules)
- `needs_plan_link` - Boolean (FAQ requires plan context)
- `needs_rule_link` - Boolean (FAQ requires rule context)
- `needs_network_check` - Boolean (FAQ requires network context)
- `requires_plan_confirmation` - Boolean (answer depends on plan terms)
- `requires_network_verification` - Boolean (answer depends on provider status)
- `ingestion_priority` - Phase 1 or Phase 2

**See METADATA_SCHEMA.json for complete field definitions.**

---

## 7. Pre-Ingestion Validation Checklist

Before ingesting any chunk file, verify:

- [ ] **File Format:** Valid JSONL (one JSON object per line)
- [ ] **Required Fields:** All mandatory fields present
- [ ] **ID Uniqueness:** No duplicate chunk_id values
- [ ] **Cross-References:** Referenced IDs exist in target files
- [ ] **Placeholder Flags:** Plans and network chunks marked `is_placeholder: true`
- [ ] **Status Values:** Valid status enums (Approved, Needs Review, Pending Detail, Active)
- [ ] **Text Content:** All chunks have non-empty text field
- [ ] **Encoding:** UTF-8 encoding (no corruption)
- [ ] **Line Count:** Expected number of chunks (see Package Inventory table)

**Validation Reference:** See `validation_report.md` in KB_PACK_V1 for detailed validation results.

---

## 8. Post-Ingestion Validation

After ingestion, verify:

- [ ] **Chunk Counts:** All expected chunks ingested (Phase 1: 67, Phase 2: 20)
- [ ] **Metadata Indexed:** All metadata fields searchable/filterable
- [ ] **Text Searchable:** Full-text search returns expected results
- [ ] **Placeholder Flags:** Can filter chunks by `is_placeholder: true`
- [ ] **Status Filters:** Can filter by status (Approved, Needs Review, etc.)
- [ ] **Weight Hints Applied:** Retrieval scoring respects weight hints
- [ ] **Cross-References Resolved:** Mapping links resolve to target chunks
- [ ] **Test Queries:** Sample FAQ queries return correct FAQ/Rule chunks

---

## 9. Ingestion Order: Step-by-Step

### Recommended Ingestion Sequence

```
Step 1: Ingest faq_chunks.jsonl
├── Load 20 FAQ chunks
├── Index metadata: chunk_id, category, status, needs_* flags
├── Index full-text: question, internal_answer, client_answer
└── Verify: All 20 chunks searchable

Step 2: Ingest rules_chunks.jsonl
├── Load 27 Rules chunks
├── Index metadata: rule_id, rule_category, status
├── Index full-text: rule_name, rule_description, client_safe_summary
└── Verify: All 27 chunks searchable

Step 3: Ingest mapping_reference.jsonl
├── Load 20 Mapping chunks
├── Index metadata: mapping_id, question_id, rule IDs, confidence
├── Index cross-references: FAQ→Rules, FAQ→Plans (if Phase 2 ingested)
└── Verify: Cross-references resolve correctly

Step 4: Test Phase 1 Retrieval
├── Run sample FAQ queries
├── Verify FAQ+Rules retrieval works
├── Verify mapping cross-references enrich context
└── Check: No placeholder content in results yet

Step 5: Ingest plans_chunks.jsonl (WITH CAUTION)
├── Load 10 Plans chunks
├── Apply metadata: is_placeholder=true, retrieval_weight_hint=0.2
├── Apply safety flags: safe_for_client_direct_use=false
└── Verify: Plans filtered from direct customer retrieval

Step 6: Ingest network_chunks.jsonl (WITH CAUTION)
├── Load 10 Network chunks
├── Apply metadata: is_placeholder=true, retrieval_weight_hint=0.2
├── Apply safety flags: safe_for_client_direct_use=false
└── Verify: Network filtered from direct customer retrieval

Step 7: Test Phase 2 Retrieval
├── Verify placeholder chunks NOT in top results
├── Verify answers include verification disclaimers when placeholders involved
├── Test filter: is_placeholder=false returns only Phase 1 content
└── Check: Guardrails prevent placeholder misrepresentation
```

---

## 10. Future Data Integration

### When to Re-Ingest

**Trigger 1: New FAQ/Rules Content**
- Add new FAQ or Rules chunks
- Re-embed new content only (incremental ingestion)
- Update mapping if new links created
- Priority: High - extends strong knowledge

**Trigger 2: Real Plan Data Available**
- **CRITICAL:** Mark old placeholder plan chunks as deprecated
- Ingest new approved plan chunks with `is_placeholder: false`
- Update mappings to reference new plan IDs
- Remove or archive old placeholder chunks
- Priority: High - removes major risk factor

**Trigger 3: Real Network/Provider Data Available**
- **CRITICAL:** Mark old placeholder network chunks as deprecated
- Ingest new verified provider chunks with `is_placeholder: false`
- Update mappings to reference new provider IDs
- Remove or archive old placeholder chunks
- Priority: High - removes major risk factor

**Trigger 4: Mapping Refinement**
- Update confidence levels (Low → Medium/High)
- Add new cross-references
- Fix incorrect links
- Priority: Medium - improves retrieval quality

**Trigger 5: Status Updates**
- FAQ/Rule status changes (Pending Detail → Approved)
- No re-embedding needed unless content changed
- Update metadata only
- Priority: Low - incremental improvement

---

## 11. Deprecation and Archival Policy

### Marking Content as Deprecated

When new data supersedes old chunks:

1. **Update Metadata:**
   - Set `status: "Deprecated"`
   - Add `deprecated_date: "YYYY-MM-DD"`
   - Add `superseded_by: "NEW-CHUNK-ID"`

2. **Remove from Active Retrieval:**
   - Exclude from search indices
   - Or apply retrieval_weight_hint = 0.0

3. **Archive (Optional):**
   - Move to separate archive collection
   - Keep for audit trail and version history

4. **Update Cross-References:**
   - Update mapping chunks to reference new IDs
   - Mark old references as deprecated

### Placeholder Sunset Policy

**When real data arrives:**
- All placeholder plan chunks → Deprecated
- All placeholder network chunks → Deprecated
- Mapping links updated to new IDs
- Old placeholder chunks archived, not deleted (for audit)

**Timeline Goal:**
- Plans: Replace within 6 months of policy finalization
- Network: Replace within 3 months of provider partnership agreements

---

## 12. Quality Control Requirements

### During Ingestion

- [ ] **Schema Validation:** All chunks match expected schema
- [ ] **Encoding Check:** UTF-8, no special character corruption
- [ ] **Link Validation:** Cross-references resolve
- [ ] **Duplicate Check:** No duplicate chunk_id values
- [ ] **Placeholder Flagging:** Plans/network marked correctly
- [ ] **Weight Assignment:** Retrieval hints applied correctly

### Post-Ingestion

- [ ] **Retrieval Testing:** Sample queries return expected chunks
- [ ] **Guardrail Testing:** Placeholder content filtered correctly
- [ ] **Cross-Reference Testing:** Mappings enrich context correctly
- [ ] **Disclaimer Testing:** Answers include required disclaimers
- [ ] **Status Filtering:** Can filter by Approved/Needs Review/Pending Detail
- [ ] **Performance Testing:** Retrieval latency acceptable

### Ongoing Monitoring

- [ ] **Retrieval Quality:** Monitor which chunks are most/least retrieved
- [ ] **Confidence Tracking:** Track low-confidence mapping performance
- [ ] **Placeholder Leak Detection:** Alert if placeholder content in customer answers
- [ ] **Feedback Loop:** Collect user feedback on answer quality
- [ ] **Content Gaps:** Identify common questions not covered by KB

---

## 13. Ingestion Anti-Patterns (DO NOT DO)

### ❌ Anti-Pattern 1: Ingest Plans/Network First
**Why Wrong:** Users could receive placeholder content before strong knowledge base exists.

### ❌ Anti-Pattern 2: Ignore Placeholder Flags
**Why Wrong:** Placeholders will be presented as confirmed facts, causing legal/regulatory risk.

### ❌ Anti-Pattern 3: Treat All Chunks Equally
**Why Wrong:** Low-confidence placeholders will rank equally with high-confidence FAQs/Rules.

### ❌ Anti-Pattern 4: Skip Metadata Indexing
**Why Wrong:** Cannot filter by status, confidence, or placeholder flags.

### ❌ Anti-Pattern 5: Ingest Without Validation
**Why Wrong:** Corrupted data, missing fields, broken cross-references will break retrieval.

### ❌ Anti-Pattern 6: Over-Weight Placeholder Chunks
**Why Wrong:** Placeholder content will dominate retrieval results.

### ❌ Anti-Pattern 7: No Guardrails on Placeholders
**Why Wrong:** RAG system will confidently state "Basic Plan covers dental" when it's placeholder data.

### ❌ Anti-Pattern 8: Update Content Without Re-Embedding
**Why Wrong:** Retrieval will return outdated text that doesn't match current chunk content.

---

## 14. Success Criteria

### Phase 1 Success (Strong Knowledge)
- ✅ 67 chunks ingested (FAQ, Rules, Mapping)
- ✅ Sample FAQ queries return correct FAQ/Rule chunks
- ✅ Retrieval confidence is high (>80% relevant for common questions)
- ✅ Cross-references work (mapping enriches FAQ context)
- ✅ No placeholder content in results

### Phase 2 Success (Placeholder Knowledge)
- ✅ 20 placeholder chunks ingested (Plans, Network)
- ✅ Placeholders filtered from direct customer retrieval
- ✅ Answers include verification disclaimers when placeholders involved
- ✅ Retrieval weight applied correctly (very low for placeholders)
- ✅ Guardrails prevent placeholder misrepresentation

### Overall Success
- ✅ All 87 chunks searchable with appropriate weights
- ✅ Strong knowledge retrieves confidently
- ✅ Placeholder knowledge supports routing but not final answers
- ✅ System ready for production with disclaimer layer
- ✅ Clear path to replace placeholders with real data

---

## 15. Policy Enforcement

### Mandatory Requirements

These requirements are **NON-NEGOTIABLE** for production deployment:

1. ✅ **Placeholder Filtering:** All `is_placeholder: true` chunks MUST be filtered from direct customer-facing retrieval OR include explicit verification disclaimers.

2. ✅ **Weight Enforcement:** Retrieval weights MUST be applied:
   - FAQ/Rules: 0.9-1.0 (high)
   - Mapping: 0.5 (medium)
   - Plans/Network: 0.2 or lower (very low)

3. ✅ **Disclaimer Requirements:** Any answer involving plan-specific or network-specific truth MUST include:
   - "Specific plan details vary. Please check your policy documents."
   - "Please verify provider network status with customer service."

4. ✅ **Validation Checks:** Pre-ingestion and post-ingestion validation MUST pass 100%.

5. ✅ **Deprecation Protocol:** When real plan/network data arrives, placeholder chunks MUST be deprecated and removed from active retrieval within 30 days.

### Optional but Recommended

- Monitor retrieval quality metrics
- Collect user feedback on answer relevance
- Track placeholder leak incidents
- Periodic content audits (quarterly)
- A/B test retrieval strategies

---

## 16. Contact and Governance

### Policy Owner
**Knowledge Engineering Team**

### Approval Authority
- Ingestion policy changes: Knowledge Engineering Lead
- Guardrail changes: Risk & Compliance Team
- Metadata schema changes: Data Architecture Team

### Review Cycle
- Policy review: Quarterly
- Urgent changes: As needed when risks identified

### Incident Response
If placeholder content leaks to customer answers:
1. Immediately filter affected chunks from retrieval
2. Investigate root cause
3. Update guardrails to prevent recurrence
4. Report to Risk & Compliance

---

## 17. Appendix: Reference Documents

### Package Documentation
- `kb_manifest.json` - Package metadata and statistics
- `README_INGESTION.md` - Comprehensive usage guide
- `validation_report.md` - Validation results (100% pass)
- `source_inventory.md` - Source file documentation

### Policy Documents (This Folder)
- `METADATA_SCHEMA.json` - Complete metadata field definitions
- `RETRIEVAL_GUARDRAILS.md` - Answer generation safety rules
- `CHUNK_PRIORITY_MATRIX.md` - Priority and confidence matrix
- `PLACEHOLDER_HANDLING_POLICY.md` - Placeholder safety policy
- `FUTURE_INGESTION_CHECKLIST.md` - Checklist for new data

---

## 18. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-19 | KB Engineering | Initial policy creation |

---

**End of Ingestion Policy**

✅ **Policy Status:** Approved for Implementation  
⚠️ **Critical Reminder:** Never present placeholder plans or network data as confirmed insurance facts.
