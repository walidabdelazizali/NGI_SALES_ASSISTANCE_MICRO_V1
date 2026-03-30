# Metadata Application Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define exactly how metadata should be attached to chunks during ingestion

---

## 1. Overview

This specification defines **how to derive and attach metadata** to each chunk from KB_PACK_V1 during RAG ingestion.

Metadata serves three critical functions:
1. **Safety** - Flags for placeholder content, direct-use suitability, caution requirements
2. **Retrieval** - Weights, priorities, confidence levels for ranking
3. **Traceability** - Source references, versioning, relationships

**Source:** RAG_POLICY_V1/METADATA_SCHEMA.json defines 40+ metadata fields. This spec provides **derivation rules** for applying those fields during ingestion.

---

## 2. Metadata Categories

### Core Fields (REQUIRED for all chunks)
- `chunk_id` - Unique identifier
- `chunk_type` - FAQ, Rules, Plans, Network, Mapping
- `source_file` - Origin JSONL file
- `source_id` - Original source identifier
- `text` - Chunk content
- `status` - Approved, Active, Needs Review, Pending Detail, Deprecated

### Safety Fields (REQUIRED for safety-critical chunks)
- `is_placeholder` - Boolean, TRUE for placeholder content
- `safe_for_client_direct_use` - Boolean, FALSE if requires caution
- `requires_plan_confirmation` - Boolean, TRUE if plan-specific
- `requires_network_verification` - Boolean, TRUE if provider-specific
- `requires_policy_caution` - Boolean, TRUE if sensitive policy language

### Retrieval Fields (REQUIRED for ranking)
- `retrieval_weight_hint` - Float 0.0-1.0, guides retrieval priority
- `ingestion_priority` - Phase 1 or Phase 2
- `confidence` - High, Medium-High, Medium, Low-Medium, Very Low

### Content Fields (OPTIONAL but recommended)
- `category` - High-level category (e.g., "Cost & Payment")
- `subcategory` - More specific (e.g., "Deductibles")
- `priority` - High, Medium, Low (business priority)
- `related_plan_type` - Generic, Individual, Family, Group, Corporate

### Dependency Flags (OPTIONAL, for cross-reference)
- `needs_plan_link` - Boolean, TRUE if content references plan
- `needs_rule_link` - Boolean, TRUE if content references rule
- `needs_network_check` - Boolean, TRUE if content references provider

### Mapping Fields (REQUIRED for Mapping chunks only)
- `question_id` - FAQ source ID
- `primary_rule_id` - Primary related rule
- `secondary_rule_id` - Secondary rule (optional)
- `related_plan_id` - Related plan (may be placeholder)
- `answer_type` - Requires Document Reference, Requires Agent Review, etc.

### Versioning Fields (RECOMMENDED for maintenance)
- `version` - e.g., "1.0"
- `created_date` - ISO 8601 date
- `updated_date` - ISO 8601 date (if revised)
- `deprecated_date` - ISO 8601 date (if deprecated)
- `superseded_by` - Chunk ID of replacement

### Plan-Specific Fields (REQUIRED for Plan chunks)
- `plan_id` - e.g., "PLAN-003"
- `plan_name` - e.g., "Basic Family Plan"
- `plan_type` - Individual, Family, Group, Corporate

### Network-Specific Fields (REQUIRED for Network chunks)
- `provider_id` - e.g., "PROV-001"
- `provider_name` - e.g., "Dubai Medical Center"
- `provider_type` - Hospital, Clinic, Pharmacy, Diagnostic Center
- `network_name` - e.g., "Premium Network" or "[PLACEHOLDER]"
- `verification_method` - How to verify current status

---

## 3. Metadata Derivation Rules

### Rule 1: Core Fields (ALWAYS REQUIRED)

#### chunk_id
**Source:** Generate unique identifier  
**Format:** `{CHUNK_TYPE}-CHUNK-{SEQUENCE}`  
**Examples:**
- `FAQ-CHUNK-001` (for FAQ-001)
- `RULE-CHUNK-005` (for RULE-005)
- `PLAN-CHUNK-003` (for PLAN-003)
- `NETWORK-CHUNK-001` (for PROV-001)
- `MAP-CHUNK-005` (for MAP-005)

**Derivation Logic:**
```
chunk_id = f"{chunk_type.upper()}-CHUNK-{sequence_number:03d}"
```

**Why:** Unique, traceable, sortable, human-readable

---

#### chunk_type
**Source:** Derived from source file  
**Values:** "FAQ", "Rules", "Plans", "Network", "Mapping"

**Derivation Logic:**
```
if source_file == "faq_chunks.jsonl": chunk_type = "FAQ"
elif source_file == "rules_chunks.jsonl": chunk_type = "Rules"
elif source_file == "plans_chunks.jsonl": chunk_type = "Plans"
elif source_file == "network_chunks.jsonl": chunk_type = "Network"
elif source_file == "mapping_reference.jsonl": chunk_type = "Mapping"
```

---

#### source_file
**Source:** Filename from KB_PACK_V1  
**Examples:** "faq_chunks.jsonl", "rules_chunks.jsonl"

**Derivation Logic:** Direct copy from file source

---

#### source_id
**Source:** Original ID from JSONL chunk  
**Examples:** "FAQ-001", "RULE-005", "PLAN-003", "PROV-001", "MAP-005"

**Derivation Logic:** Extract from JSONL field (typically `source_id` or parse from text)

**Why:** Traceability back to source file and original documentation

---

#### text
**Source:** Chunk content from JSONL

**Derivation Logic:**
- For FAQ: Combine Question + Category + Subcategory + Client Answer (customer-facing) or Internal Answer (internal use)
- For Rules: Combine Rule name + Category + Description + Client-Safe Summary (customer-facing) or full Description (internal)
- For Plans: Full text including PLACEHOLDER WARNING
- For Network: Full text including PLACEHOLDER WARNING  
- For Mapping: Full mapping text including relationships

**Customer-Facing vs Internal Text:**
- If `safe_for_client_direct_use: true`, use client-facing text variant
- If `safe_for_client_direct_use: false`, may include internal notes but should not be surfaced directly to customers

---

#### status
**Source:** Existing status field in JSONL  
**Values:** "Approved", "Active", "Needs Review", "Pending Detail", "Deprecated"

**Derivation Logic:** Direct copy from JSONL `Status` field

**By Chunk Type:**
- FAQ: Approved (9), Needs Review (7), Pending Detail (4)
- Rules: Active (26), Needs Review (1)
- Plans: ALL "Pending Detail" (placeholder status)
- Network: ALL "Pending Detail" (placeholder status)
- Mapping: ALL "Approved"

---

### Rule 2: Safety Fields (CRITICAL FOR PROTECTION)

#### is_placeholder
**Source:** Derived from chunk type and status  
**Values:** `true` or `false`  
**MANDATORY for safety**

**Derivation Logic:**
```python
if chunk_type in ["Plans", "Network"] and status == "Pending Detail":
    is_placeholder = True
else:
    is_placeholder = False
```

**Explicit Rules:**
- **ALL Plans chunks (10):** `is_placeholder: true`
- **ALL Network chunks (10):** `is_placeholder: true`
- **ALL FAQ chunks (20):** `is_placeholder: false`
- **ALL Rules chunks (27):** `is_placeholder: false`
- **ALL Mapping chunks (20):** `is_placeholder: false`

**Why:** This is the PRIMARY safety flag preventing placeholder misrepresentation. MUST be set correctly.

---

#### safe_for_client_direct_use
**Source:** Derived from chunk type, status, and is_placeholder  
**Values:** `true` or `false`  
**MANDATORY for safety**

**Derivation Logic:**
```python
if is_placeholder == True:
    safe_for_client_direct_use = False  # NEVER directly use placeholder
elif chunk_type == "Mapping":
    safe_for_client_direct_use = False  # Mapping is reference layer, not direct answer
elif chunk_type == "FAQ" and status in ["Approved", "Needs Review", "Pending Detail"]:
    safe_for_client_direct_use = True  # FAQ with disclaimers for Needs Review/Pending Detail
elif chunk_type == "Rules" and status == "Active":
    safe_for_client_direct_use = True  # Active rules safe for reasoning
elif chunk_type == "Rules" and status == "Needs Review":
    safe_for_client_direct_use = False  # RULE-008 requires compliance review
else:
    safe_for_client_direct_use = False  # Default to safe (require review)
```

**Explicit Rules by Chunk:**
- FAQ Approved (9 chunks): `true`
- FAQ Needs Review (7 chunks): `true` (with disclaimers if used)
- FAQ Pending Detail (4 chunks): `true` (with operational disclaimers)
- Rules Active (26 chunks): `true`
- Rules Needs Review (RULE-008): `false`
- Mapping (20 chunks): `false` (reference only)
- Plans placeholders (10 chunks): `false`
- Network placeholders (10 chunks): `false`

---

#### requires_plan_confirmation
**Source:** Derived from content analysis or explicit tagging  
**Values:** `true` or `false`

**Derivation Logic:**
```python
# For FAQ chunks
if "plan" in text.lower() or "coverage" in text.lower() or "benefit" in text.lower():
    requires_plan_confirmation = True
# For Mapping chunks
if related_plan_id is not None:
    requires_plan_confirmation = True
# For Plans chunks
if chunk_type == "Plans":
    requires_plan_confirmation = True
else:
    requires_plan_confirmation = False
```

**Examples:**
- FAQ-005 "Does my plan cover dental?" → `true`
- FAQ-001 "What is a deductible?" → `true` (deductibles vary by plan)
- RULE-003 "Benefit Categories" → `true` (benefits vary by plan)
- MAP-005 (links to PLAN-003) → `true`
- All Plans chunks → `true`

**Why:** Triggers disclaimer "Check your policy documents for plan-specific details"

---

#### requires_network_verification
**Source:** Derived from content analysis or explicit tagging  
**Values:** `true` or `false`

**Derivation Logic:**
```python
if chunk_type == "Network":
    requires_network_verification = True
elif "provider" in text.lower() or "hospital" in text.lower() or "clinic" in text.lower() or "network" in text.lower():
    requires_network_verification = True
else:
    requires_network_verification = False
```

**Examples:**
- FAQ-011 "How do I refill prescriptions?" → `true` (pharmacy is provider)
- All Network chunks → `true`

**Why:** Triggers disclaimer "Verify provider network status before scheduling"

---

#### requires_policy_caution
**Source:** Derived from sensitive policy content  
**Values:** `true` or `false`

**Derivation Logic:**
```python
if status == "Needs Review":
    requires_policy_caution = True
elif chunk_type == "Rules" and ("penalty" in text.lower() or "violation" in text.lower() or "compliance" in text.lower()):
    requires_policy_caution = True
else:
    requires_policy_caution = False
```

**Examples:**
- RULE-008 "Pre-existing Condition Non-Disclosure Review" → `true`
- FAQ with sensitive topics → `true`

**Why:** Extra caution for legal/compliance sensitive content

---

### Rule 3: Retrieval Fields (REQUIRED FOR RANKING)

#### retrieval_weight_hint
**Source:** Derived from chunk type, status, confidence, and is_placeholder  
**Values:** Float 0.0-1.0  
**MANDATORY for retrieval ranking**

**Derivation Matrix:**

| Chunk Type | Status | is_placeholder | Weight |
|------------|--------|----------------|--------|
| FAQ | Approved | false | 1.0 |
| FAQ | Needs Review | false | 0.95 |
| FAQ | Pending Detail | false | 0.9 |
| Rules | Active | false | 0.9 |
| Rules | Needs Review | false | 0.85 |
| Mapping | Approved, High Confidence | false | 0.6 |
| Mapping | Approved, Medium Confidence | false | 0.5 |
| Mapping | Approved, Low Confidence | false | 0.4 |
| Plans | Pending Detail | true | 0.2 |
| Network | Pending Detail | true | 0.2 |

**Pseudo-code:**
```python
if is_placeholder == True:
    retrieval_weight_hint = 0.2  # Very low for placeholders
elif chunk_type == "FAQ":
    if status == "Approved": retrieval_weight_hint = 1.0
    elif status == "Needs Review": retrieval_weight_hint = 0.95
    elif status == "Pending Detail": retrieval_weight_hint = 0.9
elif chunk_type == "Rules":
    if status == "Active": retrieval_weight_hint = 0.9
    elif status == "Needs Review": retrieval_weight_hint = 0.85
elif chunk_type == "Mapping":
    if confidence == "High": retrieval_weight_hint = 0.6
    elif confidence == "Medium": retrieval_weight_hint = 0.5
    elif confidence == "Low": retrieval_weight_hint = 0.4
else:
    retrieval_weight_hint = 0.5  # Default medium
```

**Why:** Ensures FAQ and Rules dominate retrieval, placeholders downranked

---

#### ingestion_priority
**Source:** Derived from chunk type  
**Values:** "Phase 1" or "Phase 2"

**Derivation Logic:**
```python
if chunk_type in ["FAQ", "Rules", "Mapping"]:
    ingestion_priority = "Phase 1"
elif chunk_type in ["Plans", "Network"]:
    ingestion_priority = "Phase 2"
```

**Why:** Phase 1 = strong knowledge (deploy first), Phase 2 = placeholders (deploy with caution)

---

#### confidence
**Source:** Derived from status and chunk type  
**Values:** "High", "Medium-High", "Medium", "Low-Medium", "Very Low"

**Derivation Logic:**
```python
if is_placeholder == True:
    confidence = "Very Low"
elif chunk_type == "FAQ" and status == "Approved":
    confidence = "High"
elif chunk_type == "FAQ" and status in ["Needs Review", "Pending Detail"]:
    confidence = "Medium-High"
elif chunk_type == "Rules" and status == "Active":
    confidence = "High"
elif chunk_type == "Rules" and status == "Needs Review":
    confidence = "Medium"
elif chunk_type == "Mapping":
    confidence = "Medium"  # or extract from Mapping chunk text
else:
    confidence = "Medium"
```

**Why:** Confidence level guides answer generation (high confidence = direct answer, low confidence = disclaim or defer)

---

### Rule 4: Content Fields (OPTIONAL but Recommended)

#### category
**Source:** Extract from JSONL chunk (if present)  
**Examples:** "Cost & Payment", "Eligibility & Underwriting", "Claims & Benefits Usage"

**Derivation:** Direct copy from FAQ or Rules `Category` field

---

#### subcategory
**Source:** Extract from JSONL chunk (if present)  
**Examples:** "Deductibles", "Copays", "Waiting Periods"

**Derivation:** Direct copy from FAQ `Subcategory` field

---

#### priority
**Source:** Extract from JSONL chunk (if present)  
**Values:** "High", "Medium", "Low"

**Derivation:** Direct copy from FAQ or Rules `Priority` field

**Why:** Business priority for content updates, analytics

---

#### related_plan_type
**Source:** Derived from content or explicit tagging  
**Values:** "Generic", "Individual", "Family", "Group", "Corporate"

**Examples:**
- FAQ about general deductibles → "Generic"
- Plan chunk for "Basic Individual Plan" → "Individual"
- Plan chunk for "Comprehensive Family Plan" → "Family"

**Why:** Helps with query routing (user asking about family plans)

---

### Rule 5: Dependency Flags (OPTIONAL)

#### needs_plan_link
**Source:** Derived from content or relationships  
**Values:** `true` or `false`

**Derivation:**
```python
if chunk_type == "Mapping" and related_plan_id is not None:
    needs_plan_link = True
elif "plan-specific" in text.lower() or "varies by plan" in text.lower():
    needs_plan_link = True
else:
    needs_plan_link = False
```

**Why:** Indicates answer should reference plan details

---

#### needs_rule_link
**Source:** Derived from relationships  
**Values:** `true` or `false`

**Derivation:**
```python
if chunk_type == "Mapping" and primary_rule_id is not None:
    needs_rule_link = True
else:
    needs_rule_link = False
```

**Why:** Indicates answer should reference policy rules

---

#### needs_network_check
**Source:** Derived from content  
**Values:** `true` or `false`

**Derivation:** Same as `requires_network_verification`

---

### Rule 6: Mapping Fields (REQUIRED for Mapping chunks only)

#### question_id
**Source:** Extract from Mapping chunk text  
**Example:** "FAQ-005"

**Derivation:** Parse from Mapping text (e.g., "Question: Does my plan cover dental? (FAQ-005)")

---

#### primary_rule_id
**Source:** Extract from Mapping chunk text  
**Example:** "RULE-003"

**Derivation:** Parse from Mapping text (e.g., "Primary Rule: RULE-003")

---

#### secondary_rule_id, tertiary_rule_id
**Source:** Extract from Mapping chunk text if present  
**Optional:** Not all mappings have secondary/tertiary rules

---

#### related_plan_id
**Source:** Extract from Mapping chunk text  
**Example:** "PLAN-003"

**Derivation:** Parse from Mapping text (e.g., "Related Plan: PLAN-003")

**Note:** May reference placeholder plans (with appropriate handling)

---

#### answer_type
**Source:** Extract from Mapping chunk text  
**Values:** "Requires Document Reference", "Requires Agent Review", "Direct Answer", etc.

**Derivation:** Parse from Mapping text (e.g., "Answer Type: Requires Document Reference")

**Why:** Guides answer generation behavior (defer to documents vs provide direct answer)

---

### Rule 7: Versioning Fields (RECOMMENDED)

#### version
**Source:** Set during ingestion  
**Format:** "1.0" (initial), increment for updates

**Derivation:** Default "1.0" for initial ingestion, increment on updates

---

#### created_date
**Source:** Ingestion timestamp  
**Format:** ISO 8601 (e.g., "2026-03-19")

**Derivation:** Current date at time of ingestion

---

#### updated_date
**Source:** Update timestamp  
**Format:** ISO 8601

**Derivation:** Set only if chunk is re-ingested with content changes

---

#### deprecated_date
**Source:** Deprecation timestamp  
**Format:** ISO 8601

**Derivation:** Set when chunk is marked as deprecated (e.g., placeholder replaced with real data)

---

#### superseded_by
**Source:** Replacement chunk ID  
**Example:** "PLAN-103" (real plan replacing PLAN-003 placeholder)

**Derivation:** Set when chunk is deprecated and replaced

**Why:** Maintains upgrade path when placeholder replaced with real data

---

### Rule 8: Plan-Specific Fields (REQUIRED for Plan chunks)

#### plan_id, plan_name, plan_type
**Source:** Extract from Plan chunk text  
**Examples:**
- `plan_id: "PLAN-003"`
- `plan_name: "Basic Family Plan"`
- `plan_type: "Family"`

**Derivation:** Parse from Plan text

**Note:** For placeholders, these are structural identifiers, NOT confirmed product names

---

### Rule 9: Network-Specific Fields (REQUIRED for Network chunks)

#### provider_id, provider_name, provider_type, network_name, verification_method
**Source:** Extract from Network chunk text  
**Examples:**
- `provider_id: "PROV-001"`
- `provider_name: "Dubai Medical Center"`
- `provider_type: "Hospital"`
- `network_name: "[PLACEHOLDER]"`
- `verification_method: "Call customer service or check online provider directory"`

**Derivation:** Parse from Network text

**Note:** For placeholders, network_name is usually "[PLACEHOLDER]" and verification_method emphasizes need to check authoritative source

---

## 4. Metadata Application Examples

### Example 1: FAQ Chunk (Approved)

**Source JSONL:**
```json
{
  "source_id": "FAQ-001",
  "Question": "What is a deductible?",
  "Category": "Cost & Payment",
  "Subcategory": "Deductibles",
  "Client Answer": "A deductible is the amount you pay out-of-pocket...",
  "Priority": "High",
  "Status": "Approved"
}
```

**Applied Metadata:**
```json
{
  "chunk_id": "FAQ-CHUNK-001",
  "chunk_type": "FAQ",
  "source_file": "faq_chunks.jsonl",
  "source_id": "FAQ-001",
  "text": "Question: What is a deductible?\nCategory: Cost & Payment\nSubcategory: Deductibles\nClient Answer: A deductible is the amount you pay out-of-pocket...",
  "status": "Approved",
  "is_placeholder": false,
  "safe_for_client_direct_use": true,
  "retrieval_weight_hint": 1.0,
  "ingestion_priority": "Phase 1",
  "category": "Cost & Payment",
  "subcategory": "Deductibles",
  "priority": "High",
  "requires_plan_confirmation": true,
  "requires_network_verification": false,
  "requires_policy_caution": false,
  "confidence": "High",
  "related_plan_type": "Generic",
  "version": "1.0",
  "created_date": "2026-03-19"
}
```

---

### Example 2: Rule Chunk (Active)

**Source JSONL:**
```json
{
  "source_id": "RULE-005",
  "Rule": "Waiting Period Application",
  "Category": "Eligibility & Underwriting",
  "Description": "Waiting periods are mandatory time intervals...",
  "Client-Safe Summary": "Some health insurance plans have waiting periods...",
  "Status": "Active"
}
```

**Applied Metadata:**
```json
{
  "chunk_id": "RULE-CHUNK-005",
  "chunk_type": "Rules",
  "source_file": "rules_chunks.jsonl",
  "source_id": "RULE-005",
  "text": "Rule: Waiting Period Application\nCategory: Eligibility & Underwriting\nDescription: Waiting periods are mandatory time intervals...\nClient-Safe Summary: Some health insurance plans have waiting periods...",
  "status": "Active",
  "is_placeholder": false,
  "safe_for_client_direct_use": true,
  "retrieval_weight_hint": 0.9,
  "ingestion_priority": "Phase 1",
  "category": "Eligibility & Underwriting",
  "requires_plan_confirmation": true,
  "requires_network_verification": false,
  "requires_policy_caution": true,
  "confidence": "High",
  "version": "1.0",
  "created_date": "2026-03-19"
}
```

---

### Example 3: Plan Chunk (Placeholder)

**Source JSONL:**
```json
{
  "source_id": "PLAN-003",
  "text": "IMPORTANT: This is a structural placeholder...\nPlan ID: PLAN-003\nPlan Name: Basic Family Plan\nPlan Type: Family\n...[PLACEHOLDER]...",
  "Status": "Pending Detail"
}
```

**Applied Metadata:**
```json
{
  "chunk_id": "PLAN-CHUNK-003",
  "chunk_type": "Plans",
  "source_file": "plans_chunks.jsonl",
  "source_id": "PLAN-003",
  "text": "IMPORTANT: This is a structural placeholder...\nPlan ID: PLAN-003\nPlan Name: Basic Family Plan\nPlan Type: Family\n...[PLACEHOLDER]...",
  "status": "Pending Detail",
  "is_placeholder": true,
  "safe_for_client_direct_use": false,
  "retrieval_weight_hint": 0.2,
  "ingestion_priority": "Phase 2",
  "plan_id": "PLAN-003",
  "plan_name": "Basic Family Plan",
  "plan_type": "Family",
  "category": "Plans",
  "requires_plan_confirmation": true,
  "requires_network_verification": false,
  "requires_policy_caution": true,
  "confidence": "Very Low",
  "version": "1.0",
  "created_date": "2026-03-19"
}
```

---

### Example 4: Network Chunk (Placeholder)

**Source JSONL:**
```json
{
  "source_id": "PROV-001",
  "text": "IMPORTANT: This is a structural placeholder...\nProvider ID: PROV-001\nProvider Name: Dubai Medical Center [PLACEHOLDER]\nProvider Type: Hospital\nNetwork Name: [PLACEHOLDER]...",
  "Status": "Pending Detail"
}
```

**Applied Metadata:**
```json
{
  "chunk_id": "NETWORK-CHUNK-001",
  "chunk_type": "Network",
  "source_file": "network_chunks.jsonl",
  "source_id": "PROV-001",
  "text": "IMPORTANT: This is a structural placeholder...\nProvider ID: PROV-001\nProvider Name: Dubai Medical Center [PLACEHOLDER]\nProvider Type: Hospital\nNetwork Name: [PLACEHOLDER]...",
  "status": "Pending Detail",
  "is_placeholder": true,
  "safe_for_client_direct_use": false,
  "retrieval_weight_hint": 0.2,
  "ingestion_priority": "Phase 2",
  "provider_id": "PROV-001",
  "provider_name": "Dubai Medical Center",
  "provider_type": "Hospital",
  "network_name": "[PLACEHOLDER]",
  "category": "Network",
  "requires_plan_confirmation": false,
  "requires_network_verification": true,
  "requires_policy_caution": false,
  "confidence": "Very Low",
  "verification_method": "Call customer service or check online provider directory",
  "version": "1.0",
  "created_date": "2026-03-19"
}
```

---

### Example 5: Mapping Chunk

**Source JSONL:**
```json
{
  "source_id": "MAP-005",
  "text": "Mapping: FAQ-005 to Related Rules and Plans\n\nQuestion: Does my plan cover dental? (FAQ-005)\nPrimary Rule: RULE-003\nRelated Plan: PLAN-003\nConfidence: High\nAnswer Type: Requires Document Reference",
  "Status": "Approved"
}
```

**Applied Metadata:**
```json
{
  "chunk_id": "MAP-CHUNK-005",
  "chunk_type": "Mapping",
  "source_file": "mapping_reference.jsonl",
  "source_id": "MAP-005",
  "text": "Mapping: FAQ-005 to Related Rules and Plans...",
  "status": "Approved",
  "is_placeholder": false,
  "safe_for_client_direct_use": false,
  "retrieval_weight_hint": 0.6,
  "ingestion_priority": "Phase 1",
  "question_id": "FAQ-005",
  "primary_rule_id": "RULE-003",
  "related_plan_id": "PLAN-003",
  "category": "Mapping",
  "confidence": "High",
  "answer_type": "Requires Document Reference",
  "needs_plan_link": true,
  "needs_rule_link": true,
  "needs_network_check": false,
  "requires_plan_confirmation": true,
  "requires_network_verification": false,
  "version": "1.0",
  "created_date": "2026-03-19"
}
```

---

## 5. Validation Rules

### Mandatory Validation (MUST CHECK)

**Check 1: All chunks have required core fields**
- [ ] chunk_id present and unique
- [ ] chunk_type present and valid
- [ ] source_file present
- [ ] source_id present
- [ ] text present and non-empty
- [ ] status present and valid

**Check 2: Safety fields set correctly**
- [ ] is_placeholder is boolean
- [ ] All Plans chunks have `is_placeholder: true`
- [ ] All Network chunks have `is_placeholder: true`
- [ ] All FAQ/Rules/Mapping chunks have `is_placeholder: false`
- [ ] safe_for_client_direct_use is boolean
- [ ] All placeholders have `safe_for_client_direct_use: false`

**Check 3: Retrieval weights in valid range**
- [ ] retrieval_weight_hint is float 0.0-1.0
- [ ] Placeholders have weight ≤ 0.3
- [ ] FAQ Approved has weight ≥ 0.95

**Check 4: Cross-field consistency**
- [ ] If `is_placeholder: true`, then `safe_for_client_direct_use: false`
- [ ] If `is_placeholder: true`, then `retrieval_weight_hint ≤ 0.3`
- [ ] If `chunk_type: "Plans"`, then `plan_id` present
- [ ] If `chunk_type: "Network"`, then `provider_id` present
- [ ] If `chunk_type: "Mapping"`, then `question_id` and `primary_rule_id` present

---

## 6. Implementation Checklist

### During Ingestion Pipeline Development
- [ ] Read JSONL files from KB_PACK_V1
- [ ] Parse each chunk as JSON object
- [ ] Apply metadata derivation rules per this spec
- [ ] Validate metadata completeness and consistency
- [ ] Store metadata alongside chunk text in vector DB

### Post-Ingestion Validation
- [ ] Query vector DB to retrieve sample chunks with metadata
- [ ] Verify all required fields present
- [ ] Verify safety flags set correctly (especially is_placeholder)
- [ ] Verify retrieval weights in expected ranges
- [ ] Test retrieval with weights applied

---

## 7. Document Control

**Filename:** METADATA_APPLICATION_SPEC.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- RAG_POLICY_V1/METADATA_SCHEMA.json - Field definitions
- INGESTION_SEQUENCE.md - When to apply metadata
- CHUNK_FILTERING_RULES.md - How metadata drives filtering

---

**END OF METADATA APPLICATION SPECIFICATION**

Apply these rules during ingestion to ensure safe, traceable, correctly ranked chunks.
