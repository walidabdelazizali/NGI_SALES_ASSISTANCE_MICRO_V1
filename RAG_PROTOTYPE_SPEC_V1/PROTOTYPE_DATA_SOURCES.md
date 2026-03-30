# RAG Prototype V1 - Data Sources

**Version:** 1.0  
**Date:** March 19, 2026  
**Status:** Internal Testing Only  

---

## Purpose

This document defines **exactly which source files** should be used for the internal prototype, including:
- Primary sources (high confidence, ready for use)
- Secondary sources (low confidence, context only)
- Disabled sources (excluded from this phase)
- Rationale for each categorization

**Design Principle:** Use strong knowledge (FAQ/Rules/Mapping) for primary answers, treat placeholders (Plans/Network) as weak context only.

---

## Source Directory Structure

### Knowledge Base Package Location

**Base directory:** `C:\micro-insurance-kb-v1\KB_PACK_V1`

**Contents:**
```
KB_PACK_V1/
├── faq_chunks.jsonl           (20 chunks)
├── rules_chunks.jsonl          (27 chunks)
├── mapping_reference.jsonl     (20 chunks)
├── plans_chunks.jsonl          (10 chunks)
├── network_chunks.jsonl        (10 chunks)
└── metadata/
    ├── FAQ_metadata.json
    ├── RULES_metadata.json
    ├── MAPPING_metadata.json
    ├── PLANS_metadata.json
    └── NETWORK_metadata.json
```

**Total:** 87 chunks across 5 source files

---

## Primary Prototype Sources (Phase 1)

### ✅ 1. FAQ Chunks - FULLY ENABLED

**File:** `KB_PACK_V1/faq_chunks.jsonl`  
**Chunk Count:** 20 chunks  
**Chunk IDs:** FAQ-001 through FAQ-020  
**Status:** Approved, Active, or Needs Review  
**Confidence Level:** HIGH  

**Content:**
- Customer-facing explanations of insurance concepts
- General coverage explanations (deductibles, copays, coinsurance, out-of-pocket max)
- Claim types and processes
- Member access and support
- Pre-authorization and approval workflows
- Emergency care and maternity policies
- General network concepts

**Why Primary Source:**
1. **Customer-safe wording:** Language is reviewed for customer communication
2. **High confidence:** All concepts are general insurance principles, not placeholder-dependent
3. **Broad coverage:** Answers most common "what is" and "how does" questions
4. **Ready for use:** No dependencies on real plan/network data

**Prototype Behavior:**
- ✅ Use FAQ chunks for primary answers to conceptual questions
- ✅ FAQ chunks always score highest in retrieval (weight 1.0)
- ✅ FAQ content can be stated confidently without disclaimers (for general concepts)
- ✅ Display FAQ sources with confidence level (High, Medium, Low)

**Example FAQ Chunks:**
- FAQ-001: "What is a deductible?" (general insurance concept)
- FAQ-005: "What types of dental coverage are available?" (general coverage types)
- FAQ-010: "How do I file a claim?" (general process)
- FAQ-015: "How do I verify if a provider is in-network?" (verification process, not specific providers)

---

### ✅ 2. Rules Chunks - FULLY ENABLED

**File:** `KB_PACK_V1/rules_chunks.jsonl`  
**Chunk Count:** 27 chunks  
**Chunk IDs:** RULE-001 through RULE-027  
**Status:** Active, Needs Review, or Pending Detail  
**Confidence Level:** HIGH to MEDIUM  

**Content:**
- Policy rules and benefit logic
- Eligibility requirements
- Coverage conditions and exclusions
- Approval and authorization rules
- Pre-existing condition disclosure rules
- Emergency care policies
- Maternity coverage rules
- Benefit calculation logic

**Why Primary Source:**
1. **Policy-accurate:** Derived from policy documents and benefit summaries
2. **Logic and reasoning:** Explains *why* certain rules exist and *how* they apply
3. **Enriches FAQ:** Provides deeper policy interpretation beyond general explanations
4. **Context-aware:** Can apply rules to specific scenarios

**Prototype Behavior:**
- ✅ Use Rules chunks for policy interpretation and logic
- ✅ Rules chunks score slightly lower than FAQ (weight 0.9) but still primary source tier
- ✅ Rules content provides reasoning and interpretation
- ⚠️ Some Rules may require plan confirmation disclaimers (if `requires_plan_confirmation=true`)
- ✅ Display Rules sources with reasoning context

**Example Rules Chunks:**
- RULE-003: "Benefit categories" (insurance, add-ons, well-being, assistance)
- RULE-005: "Deductible applies to inpatient and specialist visits" (rule logic)
- RULE-008: "Pre-existing condition disclosure required" (compliance rule)
- RULE-015: "Emergency care covered regardless of provider network" (emergency exception rule)

---

### ✅ 3. Mapping Chunks - ENABLED FOR CONTEXT

**File:** `KB_PACK_V1/mapping_reference.jsonl`  
**Chunk Count:** 20 chunks  
**Chunk IDs:** MAP-001 through MAP-020  
**Status:** Active  
**Confidence Level:** MEDIUM  

**Content:**
- Cross-reference relationships between FAQ and Rules
- Topic linkages (e.g., "dental coverage" FAQ links to "benefit categories" Rule)
- Conceptual mappings (e.g., "claim process" maps to "reimbursement timing")
- Related question suggestions

**Why Context Source:**
1. **Reference layer:** Mappings are chunk_id linkages, not user-friendly content
2. **Navigation aid:** Helps retrieval discover related FAQ/Rules content
3. **Enrichment:** Provides additional context for complex multi-topic questions
4. **Cross-topic awareness:** Connects insurance concepts that span multiple chunks

**Prototype Behavior:**
- ✅ Use Mapping chunks to find related FAQ/Rules content
- ✅ Mapping chunks score mid-tier (weight 0.4-0.6) - used for context, not primary facts
- ⚠️ **NEVER display mapping chunk text directly to users** (internal reference only)
- ✅ Use mappings to retrieve linked FAQ/Rules chunks, then display those instead
- ✅ Internal testing interface can show "related topics" derived from mappings

**Example Mapping Chunks:**
- MAP-001: Links FAQ-005 (dental coverage types) → RULE-003 (benefit categories) → RULE-010 (plan-specific benefits)
- MAP-008: Links FAQ-010 (claim filing process) → RULE-012 (reimbursement timing) → FAQ-011 (refill prescriptions)
- MAP-015: Links FAQ-015 (network verification) → RULE-020 (network rules) → FAQ-021 (emergency out-of-network)

**Mapping Usage Example:**
```
Query: "What dental coverage do I have?"
→ Retrieve FAQ-005 (dental coverage types) via semantic match
→ Retrieve MAP-001 which links FAQ-005 → RULE-003 (benefit categories)
→ Also retrieve RULE-003 for policy reasoning
→ Answer: Use FAQ-005 content + RULE-003 reasoning, but don't display MAP-001 text
```

---

## Secondary Prototype Sources (Phase 1)

### ⚠️ 4. Plans Chunks - CONTEXT ONLY, NOT PRIMARY SOURCE

**File:** `KB_PACK_V1/plans_chunks.jsonl`  
**Chunk Count:** 10 chunks  
**Chunk IDs:** PLAN-001 through PLAN-010  
**Status:** Pending Detail (placeholder)  
**Confidence Level:** VERY LOW  
**Safety Flags:** `is_placeholder=true`, `safe_for_client_direct_use=false`  

**Content:**
- Placeholder structural scaffolding for future real plan data
- Plan names (e.g., "Basic Family Plan", "Premium Individual Plan")
- Generic benefit structure templates
- **NOT confirmed product data** - these are illustrative examples only

**Why Secondary Source:**
1. **Placeholder-only:** No real plan benefits confirmed by product team yet
2. **Structural scaffolding:** Demonstrates future data structure, not current truth
3. **Legal liability:** Stating placeholder benefits as confirmed facts = misinformation risk
4. **Timeline:** Real plan data expected in 6 months (Phase D)

**Prototype Behavior:**
- ⚠️ **ALLOWED:** Recognize plan names for context awareness (e.g., query mentions "Basic Family Plan")
- ⚠️ **ALLOWED:** Use for question routing (recognize intent is plan-specific)
- ❌ **FORBIDDEN:** State placeholder plan benefits as confirmed product facts
- ❌ **FORBIDDEN:** Compare plans using placeholder data
- ❌ **FORBIDDEN:** Calculate costs using placeholder pricing
- ⚠️ Plans chunks score very low (weight 0.2, further downranked to effective 0.068)
- ⚠️ Customer-facing query type: Plans chunks **filtered out entirely** (mandatory)
- ⚠️ Internal query type: Plans chunks **allowed but labeled** "⚠️ PLACEHOLDER - Not confirmed product data"
- ✅ Plan-dependent questions **always require disclaimer:** "Check your policy documents or contact customer service for plan-specific details"

**Example Plans Chunks:**
- PLAN-003: "Basic Family Plan" (placeholder structure, not confirmed benefits)
- PLAN-007: "Premium Individual Plan" (placeholder structure, not confirmed benefits)

**Safe Usage Example:**
```
Query: "Does my Basic Family Plan cover dental?"
→ Retrieve FAQ-005 (dental coverage types) as primary source
→ Optionally retrieve PLAN-003 (Basic Family Plan) as weak context (recognize plan name)
→ Answer: "Dental coverage varies by plan type. Many plans include preventive dental care (cleanings, exams), and some plans include additional coverage for basic and major procedures. For specific dental coverage details for your Basic Family Plan, please check your policy documents or contact customer service."
→ Used FAQ-005 (general dental explanation) + acknowledged "Basic Family Plan" context from PLAN-003 placeholder, but did NOT state placeholder benefits as confirmed facts
```

**Unsafe Usage Example (FORBIDDEN):**
```
Query: "Does my Basic Family Plan cover dental?"
→ Retrieve PLAN-003 (Basic Family Plan placeholder)
→ Answer: "Yes, your Basic Family Plan includes preventive dental care (cleanings, exams twice yearly) and 50% coverage for basic procedures up to AED 2,000 annually." ❌ WRONG
→ Problem: Stated placeholder benefits as confirmed product facts = legal liability
```

---

### ⚠️ 5. Network Chunks - CONTEXT ONLY, NOT PRIMARY SOURCE

**File:** `KB_PACK_V1/network_chunks.jsonl`  
**Chunk Count:** 10 chunks  
**Chunk IDs:** PROV-001 through PROV-010  
**Status:** Pending Detail (placeholder)  
**Confidence Level:** VERY LOW  
**Safety Flags:** `is_placeholder=true`, `safe_for_client_direct_use=false`  

**Content:**
- Placeholder structural scaffolding for future real network data
- Provider names (e.g., "Dubai Medical Center", "Abu Dhabi General Hospital")
- Generic location and specialty templates
- **NOT confirmed provider data** - these are illustrative examples only

**Why Secondary Source:**
1. **Placeholder-only:** No real provider network confirmed by signed contracts yet
2. **Structural scaffolding:** Demonstrates future data structure, not current truth
3. **Legal liability:** Confirming placeholder network status = misinformation risk (patient could be denied or face surprise bills)
4. **Timeline:** Real network data expected in 3 months (Phase D)

**Prototype Behavior:**
- ⚠️ **ALLOWED:** Recognize provider names for context awareness (e.g., query mentions "Dubai Medical Center")
- ⚠️ **ALLOWED:** Use for question routing (recognize intent is network-specific)
- ❌ **FORBIDDEN:** Confirm placeholder provider network status
- ❌ **FORBIDDEN:** Provide appointment guidance based on placeholder data
- ❌ **FORBIDDEN:** Calculate out-of-network costs using placeholder data
- ⚠️ Network chunks score very low (weight 0.2, further downranked to effective 0.068)
- ⚠️ Customer-facing query type: Network chunks **filtered out entirely** (mandatory)
- ⚠️ Internal query type: Network chunks **allowed but labeled** "⚠️ PLACEHOLDER - Not confirmed provider data"
- ✅ Network-dependent questions **always require disclaimer:** "Verify provider network status before scheduling appointment by calling customer service or checking your member portal"

**Example Network Chunks:**
- PROV-001: "Dubai Medical Center" (placeholder structure, not confirmed network status)
- PROV-005: "Abu Dhabi General Hospital" (placeholder structure, not confirmed network status)

**Safe Usage Example:**
```
Query: "Is Dubai Medical Center in-network?"
→ Retrieve FAQ-015 (network verification process) as primary source
→ Optionally retrieve PROV-001 (Dubai Medical Center) as weak context (recognize provider name)
→ Answer: "To verify if a provider is in your network, you can: 1) Check your member portal provider directory, 2) Call customer service at [number], or 3) Ask the provider's office to verify coverage before your appointment. For Dubai Medical Center specifically, please verify network status before scheduling to avoid unexpected costs."
→ Used FAQ-015 (general verification process) + acknowledged "Dubai Medical Center" context from PROV-001 placeholder, but did NOT confirm network status as fact
```

**Unsafe Usage Example (FORBIDDEN):**
```
Query: "Is Dubai Medical Center in-network?"
→ Retrieve PROV-001 (Dubai Medical Center placeholder)
→ Answer: "Yes, Dubai Medical Center is in-network for all plans. You can book appointments directly." ❌ WRONG
→ Problem: Confirmed placeholder network status as fact = patient could face surprise bills = legal liability
```

---

## Disabled Sources (Phase 1)

### ❌ Excluded from Prototype

**None currently** - all 5 source files are ingested, but with different weights and usage rules.

**Note:** If future chunks are added to KB_PACK_V1 with status "Deprecated" or confidence "N/A", those should be excluded from prototype ingestion.

---

## Source Priority Hierarchy

### retrieval Weight Tiers

**Tier 1 - Primary Sources (Direct Answers):**
- FAQ (Approved/Active): Weight 1.0
- FAQ (Needs Review): Weight 0.95
- FAQ (Pending Detail): Weight 0.9
- Rules (Active): Weight 0.9
- Rules (Needs Review): Weight 0.85

**Tier 2 - Supporting Sources (Context/Enrichment):**
- Mapping (High): Weight 0.6
- Mapping (Medium): Weight 0.5
- Mapping (Low): Weight 0.4

**Tier 3 - Placeholder Sources (Weak Context Only):**
- Plans (Placeholder): Weight 0.2 → effective 0.068 after multipliers
- Network (Placeholder): Weight 0.2 → effective 0.068 after multipliers

**Effective Score Calculation:**
```
final_score = semantic_similarity × retrieval_weight × status_multiplier × use_case_multiplier

Example (FAQ vs Placeholder with identical semantic match):
FAQ Approved:     0.85 × 1.0 × 1.0 × 1.0 = 0.85
Plan Placeholder: 0.85 × 0.2 × 0.8 × 0.5 = 0.068

FAQ dominates by 12.5x despite identical semantic relevance
```

---

## Source Selection by Query Type

### Conceptual Insurance Questions

**Example:** "What is a deductible?"  
**Primary source:** FAQ chunks  
**Secondary source:** Rules chunks (if rule-based reasoning needed)  
**Placeholder handling:** N/A (not plan/network-dependent)  

---

### Policy/Rule Questions

**Example:** "Do I need pre-authorization for specialist visits?"  
**Primary source:** Rules chunks  
**Secondary source:** FAQ chunks (for customer-friendly wording)  
**Placeholder handling:** May require plan confirmation disclaimer if rule is plan-dependent  

---

### Plan-Specific Questions

**Example:** "Does my Basic Family Plan cover dental?"  
**Primary source:** FAQ chunks (general dental coverage explanation)  
**Secondary source:** Rules chunks (benefit categories, plan structure)  
**Placeholder handling:** Plans chunks optionally retrieved for context (recognize "Basic Family Plan" intent) but never primary source  
**Required disclaimer:** "Check your policy documents or contact customer service for plan-specific details"  

---

### Network-Specific Questions

**Example:** "Is Dubai Medical Center in-network?"  
**Primary source:** FAQ chunks (network verification process)  
**Secondary source:** Rules chunks (network rules)  
**Placeholder handling:** Network chunks optionally retrieved for context (recognize "Dubai Medical Center" intent) but never primary source  
**Required disclaimer:** "Verify provider network status before scheduling appointment"  

---

### Mixed Questions

**Example:** "What is my copay at Dubai Medical Center?"  
**Primary source:** FAQ chunks (copay explanation)  
**Secondary source:** Rules chunks (copay rules)  
**Placeholder handling:** Network chunks optionally retrieved for context but never primary source  
**Required disclaimers:** Both plan confirmation AND network verification  

---

## Source Quality Indicators

### Metadata Fields for Source Assessment

Each chunk includes metadata that indicates source quality:

**Core Fields:**
- `chunk_id`: Unique identifier
- `chunk_type`: FAQ, Rules, Mapping, Plans, Network
- `status`: Approved, Active, Needs Review, Pending Detail, Deprecated
- `confidence`: High, Medium, Low, Very Low, N/A

**Safety Fields:**
- `is_placeholder`: true/false (Plans and Network are true, others false)
- `safe_for_client_direct_use`: true/false (placeholders are false)
- `requires_plan_confirmation`: true/false
- `requires_network_verification`: true/false

**Retrieval Fields:**
- `retrieval_weight_hint`: 0.0-1.0 (suggested weight for retrieval)

**Prototype Usage:**
- Filter by `is_placeholder=false` for customer-facing query types (mandatory)
- Sort by `retrieval_weight_hint` descending
- Check `requires_plan_confirmation` and `requires_network_verification` for disclaimer requirements
- Display `confidence` level internally for QA validation

---

## Source Traceability

### Audit Trail Requirements

For every chunk used in an answer, preserve:

**Chunk-Level Traceability:**
- `chunk_id` (e.g., FAQ-005)
- `chunk_type` (e.g., FAQ)
- `status` (e.g., Approved)
- `confidence` (e.g., High)
- `is_placeholder` (e.g., false)

**Source-Level Traceability:**
- `source_file` (e.g., faq_chunks.jsonl)
- `source_id` (e.g., faq_dental_coverage_types)
- Original JSONL line number (optional but helpful for debugging)

**Answer-Level Traceability:**
- Primary chunks (top 1-3 chunks used for answer content)
- Secondary chunks (additional context chunks)
- Disclaimer triggers (which chunks triggered plan/network disclaimers)

**Internal Testing Display Example:**
```
Answer: "Dental coverage varies by plan type. Many plans include preventive dental care (cleanings, exams), and some plans include additional coverage for basic and major procedures. For specific dental coverage details for your Basic Family Plan, please check your policy documents or contact customer service."

Sources:
✅ Primary: FAQ-005 (dental coverage types) [Confidence: High]
  └─ File: faq_chunks.jsonl, ID: faq_dental_coverage_types
✅ Secondary: RULE-003 (benefit categories) [Confidence: High]
  └─ File: rules_chunks.jsonl, ID: rule_benefit_categories
⚠️ Context: PLAN-003 (Basic Family Plan - PLACEHOLDER) [Confidence: Very Low]
  └─ File: plans_chunks.jsonl, ID: plan_basic_family_placeholder
  └─ ⚠️ This is a PLACEHOLDER chunk - not confirmed product data

Disclaimers:
⚠️ Plan-specific confirmation required (triggered by query intent + PLAN-003 placeholder)
```

---

## Source Validation Checklist

### Pre-Ingestion Validation

Before ingesting source files, validate:

✅ **All 5 source files present:** faq_chunks.jsonl, rules_chunks.jsonl, mapping_reference.jsonl, plans_chunks.jsonl, network_chunks.jsonl  
✅ **Chunk count correct:** 87 total (20+27+20+10+10)  
✅ **All chunks have required metadata:** chunk_id, chunk_type, status, confidence, is_placeholder, safe_for_client_direct_use  
✅ **Placeholder flags correct:** Plans (10) and Network (10) have `is_placeholder=true`, all others `is_placeholder=false`  
✅ **Weights in valid range:** 0.0-1.0, placeholders ≤0.3  
✅ **No deprecated chunks:** All chunks have status Approved/Active/Needs Review/Pending Detail (exclude Deprecated if present)  

**Deployment blocker:** If validation fails, do NOT proceed with ingestion (see DEPLOYMENT_READINESS_GATES.md Gate A.1)

---

## Document Control

**Filename:** PROTOTYPE_DATA_SOURCES.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Internal Use Only  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md (what this prototype is)
- PROTOTYPE_SCOPE.md (in/out of scope)
- PROTOTYPE_INGEST_SET.md (exact ingest set definition)
- KB_PACK_V1/ (source data directory)
- RAG_EXECUTION_SPEC_V1/METADATA_APPLICATION_SPEC.md (metadata fields reference)

---

**END OF PROTOTYPE DATA SOURCES**

**Next Document:** [PROTOTYPE_INGEST_SET.md](PROTOTYPE_INGEST_SET.md) - Define exact chunks to ingest and configuration
