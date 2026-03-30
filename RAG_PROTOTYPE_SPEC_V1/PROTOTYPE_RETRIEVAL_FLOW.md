# Prototype Retrieval Flow Specification

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document defines the **step-by-step retrieval flow** for the internal RAG prototype, describing how a user query moves through the system from input to final response assembly.

The flow is designed to:
- Prioritize high-confidence FAQ and Rules content
- Use Mapping layers for cross-reference support
- Prevent placeholder Plans/Network from creating false certainty
- Maintain source traceability throughout the process
- Support internal testing with transparent behavior

---

## Retrieval Flow Overview

```
[User Query] 
    ↓
[Step 1: Query Normalization]
    ↓
[Step 2: FAQ Retrieval (Primary)]
    ↓
[Step 3: Rules Retrieval (Secondary)]
    ↓
[Step 4: Mapping Retrieval (Support)]
    ↓
[Step 5: Placeholder Context (Optional, Downweighted)]
    ↓
[Step 6: Source Assembly]
    ↓
[Step 7: Answer Generation with Safety Rules]
    ↓
[Step 8: Traceability Attachment]
    ↓
[Internal Response with Source References]
```

---

## Step-by-Step Flow Definition

### Step 1: Query Normalization

**Input:** Raw user query text

**Process:**
1. Convert query to lowercase for matching (preserve original for display)
2. Remove special characters that don't affect meaning
3. Identify query intent category:
   - Conceptual (e.g., "What is a deductible?")
   - Policy/Rules (e.g., "What's the copay for specialist visits?")
   - Plan-specific (e.g., "Does Basic Family Plan cover dental?")
   - Network-specific (e.g., "Is Dr. Ahmed in-network?")
   - Process/Operational (e.g., "How do I file a claim?")
   - System/Support (e.g., "How do I log in?")
4. Extract key entities (plan names, provider names, benefit types, etc.)

**Output:** 
- Normalized query text
- Intent category
- Extracted entities
- Original query (for display)

**Implementation Note:**  
For prototype, simple keyword matching is sufficient. Advanced NLP/NER can be added later.

---

### Step 2: FAQ Retrieval (Primary)

**Input:** Normalized query + intent category

**Process:**
1. Retrieve top-k FAQ chunks using semantic similarity
2. Filter by:
   - `chunk_type = "FAQ"`
   - `status IN ["Approved", "Active"]`
   - `confidence IN ["High", "Medium"]` (prefer High)
3. Apply FAQ weight boost (weight × 1.0, no penalty)
4. Rank by combined score: `semantic_similarity × retrieval_weight_hint × status_multiplier`
5. Return top 3-5 FAQ chunks

**Scoring Example:**
- FAQ-001 (Approved, High confidence): `0.88 × 1.0 × 1.0 = 0.88`
- FAQ-005 (Approved, Medium confidence): `0.85 × 0.95 × 1.0 = 0.8075`
- FAQ-011 (Pending Detail, Medium): `0.82 × 0.9 × 0.85 = 0.627`

**Output:**
- List of relevant FAQ chunks (max 5)
- Each with: chunk_id, content, score, confidence, status
- Empty list if no relevant FAQs found (confidence < 0.5)

**Traceability:**
Preserve: `source_file`, `source_chunk_id`, `retrieval_score`

---

### Step 3: Rules Retrieval (Secondary)

**Input:** Normalized query + intent category + FAQ results

**Process:**
1. Retrieve top-k Rules chunks using semantic similarity
2. Filter by:
   - `chunk_type = "Rules"`
   - `status IN ["Active", "Approved"]`
   - Exclude `status = "Deprecated"`
3. Apply Rules weight (weight × 1.0 for Active, × 0.95 for Needs Review)
4. If FAQ results found, boost Rules that provide reasoning for those FAQs
5. Rank by combined score
6. Return top 2-4 Rules chunks

**Cross-Linking Logic:**
- If FAQ-005 mentions "dental coverage categories", boost RULE-003 (benefit categories)
- If FAQ-015 mentions "in-network verification", boost RULE-012 (network rules)

**Output:**
- List of relevant Rules chunks (max 4)
- Each with: chunk_id, content, score, status, related FAQ IDs
- Empty list if no relevant Rules found

**Traceability:**
Preserve: `source_file`, `source_chunk_id`, `retrieval_score`, `related_faq_chunks`

---

### Step 4: Mapping Retrieval (Support)

**Input:** Normalized query + FAQ results + Rules results

**Process:**
1. Retrieve Mapping chunks that link FAQ ↔ Rules
2. Filter by:
   - `chunk_type = "Mapping"`
   - Related to already-retrieved FAQ or Rules chunks
3. Apply Mapping weight (weight × 0.5, downweighted for support role)
4. Use Mapping to identify additional FAQ/Rules that weren't retrieved yet
5. Return top 1-3 Mapping chunks

**Use Cases for Mapping:**
- **Cross-reference discovery:** FAQ-001 mentions deductible → MAP-001 links to RULE-001 (cost-sharing) → retrieve RULE-001 if not already retrieved
- **Related topic suggestion:** User asks about "maternity" → MAP-007 links maternity FAQ to pre-existing condition Rules
- **Clarification routing:** User asks vague question → Mapping helps identify which FAQ cluster is relevant

**Important:**  
Mapping chunks are **never displayed directly** to users. They are used only to:
- Find related FAQ/Rules
- Provide internal context for answer generation
- Support cross-topic reasoning

**Output:**
- List of Mapping chunks (max 3)
- Each with: chunk_id, related_faq_ids, related_rule_ids, confidence
- Suggestions for additional FAQ/Rules to retrieve

**Traceability:**
Preserve: `source_file`, `source_chunk_id`, `linked_chunks`

---

### Step 5: Placeholder Context (Optional, Downweighted)

**Input:** Normalized query + all previous results + intent category

**Process:**
1. **Only if** query is plan-specific or network-specific:
   - Retrieve Plans chunks (`chunk_type = "Plans"`)
   - Retrieve Network chunks (`chunk_type = "Network"`)
2. Filter by:
   - `is_placeholder = TRUE` (all Plans/Network are placeholders in Phase 1)
   - `safe_for_client_direct_use = FALSE`
3. Apply heavy placeholder penalty:
   - Weight: `retrieval_weight_hint × 0.2` (5x downweighted)
   - Use case penalty: `× 0.5` (internal testing)
   - Combined: `semantic_similarity × 0.2 × 0.8 × 0.5 = semantic × 0.08`
4. Retrieve top 1-2 placeholder chunks **for context only**

**Scoring Example:**
- PLAN-003 (Basic Family Plan placeholder): `0.85 × 0.2 × 0.8 × 0.5 = 0.068`
- Compared to FAQ-005: `0.85 × 1.0 × 1.0 × 1.0 = 0.85`
- **FAQ scores 12.5x higher** even with identical semantic match

**Critical Rules:**
- ❌ **DO NOT use placeholder content to state final plan benefits**
- ❌ **DO NOT use placeholder content to confirm provider network status**
- ✅ **DO use placeholder to recognize plan/provider names mentioned in query**
- ✅ **DO use placeholder to route to correct FAQ topic (e.g., "dental" topic)**

**Output:**
- List of placeholder chunks (max 2)
- Each with: chunk_id, content, score, **WARNING: PLACEHOLDER** label
- Metadata: `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`

**Traceability:**
Preserve: `source_file`, `source_chunk_id`, `retrieval_score`, `placeholder_warning`

---

### Step 6: Source Assembly

**Input:** All retrieved chunks from Steps 2-5

**Process:**
1. Combine all retrieved chunks into a single source collection
2. Sort by retrieval score (highest first)
3. Group by chunk type:
   - **Primary sources:** FAQ + Rules (high confidence)
   - **Support sources:** Mapping (context only)
   - **Context sources:** Placeholders (recognition only, never as truth)
4. Calculate overall confidence tier:
   - **Tier 1 (Strongest):** FAQ + Rules only, no placeholders
   - **Tier 2 (Strong):** FAQ + Rules + Mapping, no placeholders
   - **Tier 3 (Moderate):** FAQ + Rules + Placeholders present
   - **Tier 4 (Weak):** Rules only, no FAQ
   - **Tier 5 (Unsafe):** Placeholders only, no FAQ/Rules

**Confidence Determination Rule (Weakest Link):**
Overall confidence = **MIN(confidence of all chunks in primary/context sources)**

**Example:**
- Retrieved: FAQ-005 (High confidence), RULE-003 (Medium confidence), PLAN-003 (placeholder Low confidence)
- Overall confidence = MIN(High, Medium, Low) = **Low**
- Rationale: Placeholder drags down confidence even if FAQ is strong
- **Action:** Answer must reflect Low confidence with caution language

**Output:**
- Assembled source collection with:
  - Primary sources (FAQ/Rules)
  - Support sources (Mapping)
  - Context sources (Placeholders)
  - Overall confidence tier
  - Weakest link identified

**Traceability:**
Preserve all source metadata for final response

---

### Step 7: Answer Generation with Safety Rules

**Input:** Source assembly + original query + overall confidence tier

**Process:**

#### 7.1 Determine Answer Strategy

Based on overall confidence tier:

**Tier 1 (FAQ + Rules only):**
- Strategy: Confident, direct answer
- Use FAQ wording for customer-friendly language
- Use Rules for policy reasoning
- Minimal disclaimers needed
- Example: "A deductible is the amount you pay out-of-pocket before insurance coverage begins..."

**Tier 2 (FAQ + Rules + Mapping):**
- Strategy: Confident answer with cross-references
- Use Mapping to enrich context
- Follow Tier 1 approach
- Example: "Dental coverage varies by plan tier. Related topics: benefit categories, cost-sharing..."

**Tier 3 (FAQ + Rules + Placeholders):**
- Strategy: Moderate caution, general guidance only
- Use FAQ/Rules for general concepts
- Recognize plan/provider from placeholder BUT DON'T state placeholder details as facts
- **Mandatory disclaimer:** "Check your policy documents for plan-specific details"
- Example: "Dental coverage typically includes preventive care, and some plans include restorative procedures. For your Basic Family Plan specifically, check your policy documents or contact customer service."

**Tier 4 (Rules only, no FAQ):**
- Strategy: Policy guidance with caution
- Provide policy reasoning from Rules
- Add disclaimer about limited FAQ coverage
- Example: "Policy generally requires pre-existing condition disclosure. For customer-friendly guidance, contact customer service."

**Tier 5 (Placeholders only, no FAQ/Rules):**
- Strategy: Safe fallback, refuse to answer with certainty
- **DO NOT generate answer from placeholder content**
- Provide contact information instead
- Example: "I don't have reliable information on that specific topic. Please contact customer service at [number] for accurate information."

#### 7.2 Apply Safety Rules

For all answers:
1. **Check for plan confirmation requirement:**
   - If `requires_plan_confirmation = TRUE` in any source → add disclaimer
   - Disclaimer: "Coverage details vary by plan. Check your policy documents or contact customer service."

2. **Check for network verification requirement:**
   - If `requires_network_verification = TRUE` in any source → add disclaimer
   - Disclaimer: "Provider network status may vary. Verify with customer service before scheduling appointment."

3. **Check for operational process questions:**
   - If query is about operational process (claims, refills, support) → add disclaimer
   - Disclaimer: "Contact customer service at [number] for step-by-step instructions specific to your situation."

4. **Check for placeholder presence:**
   - If any placeholder in sources → add caution
   - Caution: "This answer includes general guidance. For specific details about your plan or provider, verify with customer service."

5. **Check for low confidence:**
   - If overall confidence = Low or Very Low → add strong disclaimer
   - Disclaimer: "I have limited information on this topic. For accurate details, contact customer service at [number]."

#### 7.3 Generate Answer Text

1. Start with direct answer from primary sources (FAQ/Rules)
2. Provide reasoning if available from Rules
3. Add context from Mapping if helpful (related topics)
4. Add disclaimers based on safety rules above
5. Provide contact information if needed
6. Keep answer concise (2-4 paragraphs max for prototype)

**Answer Quality Guidelines:**
- Use customer-friendly language from FAQ chunks
- Be honest about limitations
- Never overstate certainty
- Prefer "typically" and "generally" over "always" when near placeholders
- Explicitly state when plan confirmation or network verification is required

**Output:**
- Generated answer text
- List of applied disclaimers
- Confidence tier label
- Safety rules triggered

---

### Step 8: Traceability Attachment

**Input:** Generated answer + all source chunks

**Process:**
1. Attach full source traceability to the answer (internal only, not shown to end user in prototype)
2. Include for each source chunk:
   - `chunk_id` (e.g., FAQ-001, RULE-005, PLAN-003)
   - `source_file` (e.g., faq_chunks.jsonl)
   - `source_chunk_id` (original ID from KB_PACK_V1)
   - `chunk_type` (FAQ, Rules, Mapping, Plans, Network)
   - `retrieval_score` (0.0-1.0)
   - `confidence` (High, Medium, Low)
   - `status` (Approved, Active, Pending Detail)
   - `is_placeholder` (TRUE/FALSE)
   - `safe_for_client_direct_use` (TRUE/FALSE)
   - `content_preview` (first 100 chars)
3. Attach metadata:
   - `overall_confidence_tier` (Tier 1-5)
   - `weakest_link_chunk_id` (which chunk dragged down confidence)
   - `disclaimers_applied` (list)
   - `safety_rules_triggered` (list)
4. Attach query metadata:
   - `original_query`
   - `normalized_query`
   - `intent_category`
   - `timestamp`

**Output:**
- Complete internal response object with:
  - `answer_text` (what user sees)
  - `sources` (array of source chunks)
  - `metadata` (confidence, disclaimers, etc.)
  - `traceability` (full audit trail)

**Purpose:**
- Internal testing can review which sources were used
- Identify when placeholders influenced answer
- Debug retrieval quality issues
- Validate safety rules are firing correctly
- Support future content improvement (identify FAQ gaps)

---

## Final Internal Response Structure

```json
{
  "query": {
    "original": "Does my Basic Family Plan cover dental?",
    "normalized": "basic family plan cover dental",
    "intent_category": "plan-specific",
    "timestamp": "2026-03-20T10:15:00Z"
  },
  "answer": {
    "text": "Dental coverage varies by plan type and tier. Many plans include preventive dental care (cleanings, exams), and some plans include additional coverage for basic and major procedures.\n\nFor specific dental coverage details for your Basic Family Plan, please:\n- Check your policy documents or benefits summary\n- Contact customer service at [number]\n- Log into your member portal\n\n**Note:** Coverage details vary by plan. Check your policy documents or contact customer service.",
    "confidence_tier": "Tier 3 (Moderate)",
    "disclaimers_applied": [
      "requires_plan_confirmation",
      "placeholder_present"
    ],
    "safety_rules_triggered": [
      "Plan confirmation required",
      "Placeholder context included"
    ]
  },
  "sources": [
    {
      "chunk_id": "FAQ-005",
      "source_file": "faq_chunks.jsonl",
      "chunk_type": "FAQ",
      "retrieval_score": 0.88,
      "confidence": "High",
      "status": "Approved",
      "is_placeholder": false,
      "safe_for_client_direct_use": true,
      "content_preview": "**Q: What types of dental coverage are available?** A: Dental coverage varies by plan..."
    },
    {
      "chunk_id": "RULE-003",
      "source_file": "rules_chunks.jsonl",
      "chunk_type": "Rules",
      "retrieval_score": 0.72,
      "confidence": "Medium",
      "status": "Active",
      "is_placeholder": false,
      "safe_for_client_direct_use": true,
      "content_preview": "Benefit categories are organized into tiers: preventive, basic, major..."
    },
    {
      "chunk_id": "PLAN-003",
      "source_file": "plans_chunks.jsonl",
      "chunk_type": "Plans",
      "retrieval_score": 0.068,
      "confidence": "Low",
      "status": "Pending Detail",
      "is_placeholder": true,
      "safe_for_client_direct_use": false,
      "content_preview": "**Basic Family Plan** [PLACEHOLDER] - Awaiting product team finalization..."
    }
  ],
  "metadata": {
    "overall_confidence_tier": "Tier 3 (Moderate)",
    "weakest_link_chunk_id": "PLAN-003",
    "primary_source_count": 2,
    "placeholder_count": 1,
    "mapping_count": 0
  },
  "traceability": {
    "retrieval_timestamp": "2026-03-20T10:15:00.123Z",
    "retrieval_duration_ms": 245,
    "faq_retrieved": 1,
    "rules_retrieved": 1,
    "placeholders_retrieved": 1,
    "total_sources": 3
  }
}
```

---

## Retrieval Flow Variations by Query Type

### Conceptual Question (e.g., "What is a deductible?")

**Flow:**
1. Query normalized → intent: conceptual
2. FAQ retrieval → FAQ-001 (High confidence, score 0.92)
3. Rules retrieval → RULE-001 (supporting reasoning, score 0.68)
4. Mapping retrieval → MAP-001 (links to related cost-sharing concepts)
5. Placeholder retrieval → **SKIPPED** (not relevant)
6. Source assembly → Tier 1 (FAQ + Rules only, no placeholders)
7. Answer generation → Confident direct answer, minimal disclaimers
8. Traceability attached

**Result:** Clean, confident answer with strong sources

---

### Plan-Specific Question (e.g., "Does Basic Family Plan cover maternity?")

**Flow:**
1. Query normalized → intent: plan-specific, entity: "Basic Family Plan"
2. FAQ retrieval → FAQ-007 (maternity coverage general, score 0.85)
3. Rules retrieval → RULE-009 (maternity rules, score 0.78)
4. Mapping retrieval → MAP-007 (links maternity to pre-existing conditions)
5. Placeholder retrieval → PLAN-003 (Basic Family Plan placeholder, score 0.068)
6. Source assembly → Tier 3 (FAQ + Rules + Placeholder present)
7. Answer generation → General guidance from FAQ/Rules, recognize "Basic Family Plan" from placeholder BUT DON'T state placeholder details, **mandatory disclaimer** "check your policy documents"
8. Traceability attached with placeholder warning

**Result:** Cautious answer, placeholder recognized but not trusted, strong disclaimer

---

### Network-Specific Question (e.g., "Is Dr. Ahmed in-network?")

**Flow:**
1. Query normalized → intent: network-specific, entity: "Dr. Ahmed"
2. FAQ retrieval → FAQ-015 (network verification process, score 0.88)
3. Rules retrieval → RULE-012 (network rules, score 0.71)
4. Mapping retrieval → MAP-015 (links network to billing/reimbursement)
5. Placeholder retrieval → PROV-002 (provider placeholder, score 0.072)
6. Source assembly → Tier 3 (FAQ + Rules + Placeholder present)
7. Answer generation → Provide FAQ network verification process, recognize "Dr. Ahmed" from placeholder BUT DON'T confirm network status, **mandatory disclaimer** "verify before appointment"
8. Traceability attached with placeholder warning

**Result:** Process guidance answer, provider recognized but NOT confirmed, strong verification disclaimer

---

## Monitoring Points for Internal Testing

During internal testing, monitor:

1. **Retrieval Quality:**
   - Are relevant FAQ chunks in top 3?
   - Are Rules chunks providing useful reasoning?
   - Are Mapping chunks identifying correct cross-references?

2. **Placeholder Behavior:**
   - Are placeholders properly downweighted (score <0.1)?
   - Is placeholder content NEVER stated as confirmed fact?
   - Are disclaimers firing when placeholders present?

3. **Confidence Tier Distribution:**
   - What % of queries result in Tier 1 (strongest)?
   - What % fall to Tier 3 (moderate caution)?
   - What % fall to Tier 5 (unsafe fallback)?

4. **Disclaimer Appropriateness:**
   - Are disclaimers added when needed?
   - Are disclaimers NOT added when unnecessary (Tier 1 queries)?

5. **Answer Quality:**
   - Are answers using customer-friendly FAQ wording?
   - Are answers providing sufficient reasoning from Rules?
   - Are answers honest about limitations?

6. **Traceability Completeness:**
   - Can every answer be traced back to source chunks?
   - Is weakest link correctly identified?
   - Are safety rules correctly logged?

---

## Implementation Notes for Engineering

### Prototype Phase 1 Simplifications

For the internal prototype, engineering can simplify:

1. **Semantic Similarity:**
   - Simple embedding model (e.g., sentence-transformers/all-MiniLM-L6-v2) is sufficient
   - More advanced models can be added later

2. **Query Normalization:**
   - Basic text preprocessing (lowercase, strip punctuation)
   - Simple keyword matching for intent classification
   - Advanced NLP/NER can be added later

3. **Ranking Formula:**
   - Start with simple: `semantic_similarity × retrieval_weight_hint × status_multiplier`
   - Advanced BM25 + semantic hybrid can be added later

4. **Answer Generation:**
   - Template-based generation is sufficient for prototype
   - LLM-based generation (GPT-4, Claude) can be added later
   - Templates should reference source chunks directly

5. **Traceability:**
   - Store full trace in JSON format
   - Display in internal testing UI for review
   - Production version can optimize storage

### Critical Implementation Requirements

These MUST be implemented correctly even in prototype:

1. ✅ **Placeholder downweighting:** Score <0.1 for all placeholders
2. ✅ **Disclaimer firing:** Mandatory when placeholders present or plan/network confirmation required
3. ✅ **Weakest link rule:** Overall confidence = MIN of all source confidences
4. ✅ **Source traceability:** Every answer must trace back to source chunks
5. ✅ **Tier 5 fallback:** If only placeholders retrieved, refuse to answer with certainty

### Testing the Retrieval Flow

To validate the flow is working:

1. **Test with conceptual query:** Should produce Tier 1 answer (confident, no disclaimers)
2. **Test with plan-specific query:** Should produce Tier 3 answer (cautious, with disclaimer)
3. **Test with network-specific query:** Should produce Tier 3 answer (process guidance, verification disclaimer)
4. **Test with unsupported topic:** Should produce Tier 5 answer (safe fallback, contact service)
5. **Inspect traceability:** Verify all sources are logged correctly

---

## Document Control

**Filename:** PROTOTYPE_RETRIEVAL_FLOW.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_SCOPE.md - What is in/out of scope
- PROTOTYPE_DATA_SOURCES.md - Which files to ingest
- PROTOTYPE_INGEST_SET.md - What to ingest first
- PROTOTYPE_QUERY_HANDLING.md - Query type strategies (next)
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Answer generation rules (next)
- HANDOFF_TO_ENGINEERING.md - Implementation handoff

---

**END OF RETRIEVAL FLOW SPECIFICATION**
