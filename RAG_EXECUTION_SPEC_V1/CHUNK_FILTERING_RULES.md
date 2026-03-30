# Chunk Filtering Rules Specification

**Version:** 1.0  
**Date:** March 19, 2026  
**Purpose:** Define which chunks are allowed, downranked, or filtered based on metadata and use case

---

## 1. Overview

This specification defines **filtering and downranking rules** to apply during RAG retrieval.

Filtering serves three critical functions:
1. **Safety** - Prevent placeholder content from being presented as confirmed facts
2. **Relevance** - Prioritize strong knowledge (FAQ/Rules) over weak knowledge (placeholders)
3. **Use Case Adaptation** - Different filtering for customer-facing vs internal use

---

## 2. Filtering Philosophy

### Truth Hierarchy (NON-NEGOTIABLE)

**Tier 1: Strong Knowledge (Always Eligible)**
- FAQ (Approved, Needs Review, Pending Detail with disclaimers)
- Rules (Active, Needs Review with caution)
- **Use:** Primary retrieval, direct customer answers

**Tier 2: Reference Knowledge (Context Enrichment)**
- Mapping (High/Medium/Low Confidence)
- **Use:** Cross-reference support, relationship awareness, NOT direct customer display

**Tier 3: Placeholder Knowledge (Routing Awareness Only)**
- Plans (ALL placeholders)
- Network (ALL placeholders)
- **Use:** Question routing, context awareness, gap identification
- **NEVER:** Direct customer answers, benefit confirmation, provider verification

---

## 3. Use Case-Specific Filtering

### Use Case 1: Customer-Facing Chatbot (STRICT FILTERING)

**Goal:** Provide safe, verified answers to customers

**Filtering Rules:**

#### Rule 1: Mandatory Placeholder Exclusion
**Filter OUT:**
- All chunks where `is_placeholder: true`

**Rationale:** Placeholders are NOT confirmed product/provider data. Presenting them as facts = legal liability.

**Implementation:**
```
WHERE is_placeholder = false
```

**Exception:** If placeholder-aware context is needed (e.g., "We don't have your plan details yet"), explicitly handle in answer generation, NOT retrieval. Do not retrieve placeholders for customer-facing answers.

---

#### Rule 2: Status-Based Filtering (OPTIONAL but RECOMMENDED)
**Prefer:**
- `status: "Approved"` or `status: "Active"`

**Downrank:**
- `status: "Needs Review"` (reduce weight by 10%)
- `status: "Pending Detail"` (reduce weight by 20%, add disclaimers)

**Filter OUT:**
- `status: "Deprecated"` (completely exclude)

**Implementation:**
```
WHERE status IN ('Approved', 'Active', 'Needs Review', 'Pending Detail')
ORDER BY 
  CASE status
    WHEN 'Approved' THEN 1.0
    WHEN 'Active' THEN 1.0
    WHEN 'Needs Review' THEN 0.9
    WHEN 'Pending Detail' THEN 0.8
  END * retrieval_weight_hint DESC
```

---

#### Rule 3: Safe-for-Client Filter (STRONG RECOMMENDATION)
**Prefer:**
- `safe_for_client_direct_use: true`

**Downrank or Exclude:**
- `safe_for_client_direct_use: false` (Mapping, RULE-008, all placeholders)

**Rationale:** Chunks marked unsafe should not be directly shown to customers without expert review.

**Implementation:**
```
WHERE safe_for_client_direct_use = true
OR (safe_for_client_direct_use = false AND use_as_context_only = true)
```

---

#### Rule 4: Mapping Exclusion from Direct Display
**Filter OUT from direct customer answers:**
- All chunks where `chunk_type: "Mapping"`

**Allow for context enrichment:**
- Mapping CAN be retrieved to understand relationships (e.g., FAQ-005 → RULE-003)
- Mapping should NOT appear in final answer text shown to customer

**Implementation:**
```
# Retrieval: Include Mapping for cross-reference
WHERE chunk_type IN ('FAQ', 'Rules', 'Mapping')

# Answer Display: Exclude Mapping from visible text
display_chunks = [c for c in retrieved_chunks if c.chunk_type != 'Mapping']
```

---

### Use Case 2: Internal Knowledge Assistant (MODERATE FILTERING)

**Goal:** Provide comprehensive context to support staff (customer service, underwriters, compliance)

**Filtering Rules:**

#### Rule 1: Include Placeholders with Warnings
**Allow:**
- All chunks including placeholders (`is_placeholder: true`)

**Requirement:**
- Add clear warning labels: "⚠️ PLACEHOLDER - Not confirmed product data"
- Use lower retrieval weight (0.2)
- Display placeholder status prominently

**Rationale:** Support staff may benefit from knowing structure even if data is not final, but must understand it's not confirmed.

---

#### Rule 2: Include Mapping for Cross-Reference
**Allow:**
- All chunk types including Mapping

**Use:**
- Show relationships (FAQ → Rules → Plans)
- Help staff understand knowledge structure

---

#### Rule 3: Show Deprecated Content (OPTIONAL)
**Allow:**
- `status: "Deprecated"` chunks (with clear labeling)

**Rationale:** Helps staff understand what's changed, historical context

---

### Use Case 3: Self-Service FAQ Portal (VERY STRICT FILTERING)

**Goal:** Provide only the most reliable, approved FAQ answers

**Filtering Rules:**

#### Rule 1: FAQ Approved Only
**Allow ONLY:**
- `chunk_type: "FAQ"` AND `status: "Approved"`

**Filter OUT:**
- All Rules (too complex for self-service)
- All Mapping (not customer-facing)
- All Placeholders
- FAQ Needs Review or Pending Detail (not ready for unassisted self-service)

**Implementation:**
```
WHERE chunk_type = 'FAQ' AND status = 'Approved'
```

---

#### Rule 2: High Confidence Only
**Require:**
- `confidence: "High"`
- `safe_for_client_direct_use: true`

**Rationale:** Self-service means no human in the loop to add disclaimers or context. Only highest confidence content allowed.

---

### Use Case 4: Developer Testing/QA (NO FILTERING)

**Goal:** Test retrieval across all chunk types

**Filtering Rules:**
- **NONE** - Retrieve everything to test system completeness

**Use:**
- Validate ingestion (all 87 chunks indexed)
- Test placeholder handling
- Verify metadata application
- Debug retrieval issues

**Warning:** Never deploy "no filtering" to customer-facing environment.

---

## 4. Retrieval Weight Enforcement

### Base Retrieval Weights (from METADATA_APPLICATION_SPEC.md)

| Chunk Type | Status | is_placeholder | Base Weight |
|------------|--------|----------------|-------------|
| FAQ | Approved | false | 1.0 |
| FAQ | Needs Review | false | 0.95 |
| FAQ | Pending Detail | false | 0.9 |
| Rules | Active | false | 0.9 |
| Rules | Needs Review | false | 0.85 |
| Mapping | High Confidence | false | 0.6 |
| Mapping | Medium Confidence | false | 0.5 |
| Mapping | Low Confidence | false | 0.4 |
| Plans | Pending Detail | true | 0.2 |
| Network | Pending Detail | true | 0.2 |

### Weight Penalties (Apply on Top of Base Weight)

**Penalty 1: Placeholder Penalty**
- If `is_placeholder: true`, cap weight at 0.3 maximum
- Ensures placeholders never outrank FAQ/Rules even with good semantic match

**Penalty 2: Low Confidence Penalty**
- If `confidence: "Low"` or `confidence: "Very Low"`, reduce weight by 30%

**Penalty 3: Needs Review Penalty**
- If `status: "Needs Review"`, reduce weight by 5-10%

**Penalty 4: Pending Detail Penalty**
- If `status: "Pending Detail"`, reduce weight by 10-20%

**Penalty 5: Safe-for-Client Penalty (Optional)**
- If `safe_for_client_direct_use: false`, reduce weight by 50% for customer-facing retrieval

---

### Final Retrieval Score Calculation

```python
final_score = semantic_similarity_score * retrieval_weight_hint * penalty_multiplier

# Example for FAQ Approved (strong knowledge):
final_score = 0.85 * 1.0 * 1.0 = 0.85

# Example for Plan Placeholder (weak knowledge):
final_score = 0.85 * 0.2 * 1.0 = 0.17  # Heavily downranked

# Example for Mapping Medium Confidence:
final_score = 0.75 * 0.5 * 1.0 = 0.375
```

**Result:** Even if placeholder has identical semantic match (0.85) as FAQ, FAQ scores 0.85 while placeholder scores 0.17. FAQ wins by 5x.

---

## 5. Filtering Rules by Chunk Type

### FAQ Chunks (20 total)

**Customer-Facing:**
- ✅ Allow: All FAQ chunks (Approved, Needs Review, Pending Detail)
- ⚠️ Caution: Add disclaimers for Needs Review or Pending Detail
- ❌ Block: None (all FAQ chunks have real content, just varying completeness)

**Retrieval Weight:**
- Approved: 1.0 (highest priority)
- Needs Review: 0.95
- Pending Detail: 0.9

**Specific Affected FAQs:**
- FAQ-011, FAQ-013, FAQ-017, FAQ-020: Status "Pending Detail" → Add operational disclaimer ("Contact customer service for specific instructions")

---

### Rules Chunks (27 total)

**Customer-Facing:**
- ✅ Allow: Rules with `status: "Active"` (26 chunks)
- ⚠️ Caution: RULE-008 (`status: "Needs Review"`) → Requires compliance review before direct customer use

**Retrieval Weight:**
- Active: 0.9
- Needs Review: 0.85

**Specific Affected Rules:**
- RULE-008 "Pre-existing Condition Non-Disclosure Review" → May need to be excluded from customer-facing retrieval until compliance approval

---

### Mapping Chunks (20 total)

**Customer-Facing:**
- ✅ Allow: Retrieve for cross-reference context
- ❌ Block: Never display Mapping chunks directly to customers (reference layer only)

**Retrieval Weight:**
- High Confidence: 0.6
- Medium Confidence: 0.5
- Low Confidence: 0.4

**Specific Affected Mappings:**
- MAP-012, MAP-013, MAP-017: Low Confidence → Use with extra caution, may add disclaimer if primary evidence

**Usage Pattern:**
```python
# Retrieve Mapping for cross-reference
mapping = retrieve_mapping(faq_id="FAQ-005")

# Use Mapping to find related Rule
rule = retrieve_rule(rule_id=mapping.primary_rule_id)

# Display FAQ + Rule to customer (NOT Mapping text)
answer = generate_answer(faq_text + rule_text)
```

---

### Plans Chunks (10 total - ALL PLACEHOLDERS)

**Customer-Facing:**
- ❌ Block: ALL Plans chunks have `is_placeholder: true`
- **NEVER** present as confirmed plan benefits

**Internal Use:**
- ✅ Allow: For question routing and context awareness with warnings

**Retrieval Weight:**
- ALL: 0.2 (very low)

**Filtering Rule (MANDATORY for customer-facing):**
```python
WHERE NOT (chunk_type = 'Plans' AND is_placeholder = true)
```

**Allowed Use Cases:**
1. **Question Routing:** "User is asking about Basic Family Plan" → Route to plan-specific support
2. **Context Awareness:** System understands "Basic Family Plan" exists (structurally) but doesn't have confirmed benefits
3. **Gap Identification:** "We don't have benefit details for this plan yet" → Defer to customer service

**Forbidden Use Cases:**
1. ❌ "Basic Family Plan covers dental" (benefit confirmation)
2. ❌ "Basic Family Plan costs AED 600/month" (cost statement)
3. ❌ "Basic Family Plan has AED 500 deductible" (plan detail)
4. ❌ Comparing plans based on placeholder data

---

### Network Chunks (10 total - ALL PLACEHOLDERS)

**Customer-Facing:**
- ❌ Block: ALL Network chunks have `is_placeholder: true`
- **NEVER** confirm provider network status

**Internal Use:**
- ✅ Allow: For question routing and context awareness with warnings

**Retrieval Weight:**
- ALL: 0.2 (very low)

**Filtering Rule (MANDATORY for customer-facing):**
```python
WHERE NOT (chunk_type = 'Network' AND is_placeholder = true)
```

**Allowed Use Cases:**
1. **Question Routing:** "User is asking about Dubai Medical Center" → Route to network verification support
2. **Context Awareness:** System understands "Dubai Medical Center" is a hospital type
3. **Gap Identification:** "We need to verify provider network status" → Direct to provider directory or customer service

**Forbidden Use Cases:**
1. ❌ "Dubai Medical Center is in-network" (network confirmation)
2. ❌ "Visit Dubai Medical Center for treatment" (provider recommendation)
3. ❌ "Dubai Medical Center accepts your plan" (network status)
4. ❌ Listing providers based on placeholder data

---

## 6. Multi-Query Filtering (Advanced)

### Scenario: User Asks "Does my Basic Family Plan cover dental?"

**Query Analysis:**
- Intent: Plan-specific benefit question
- Entities: "Basic Family Plan", "dental coverage"

**Retrieval Strategy:**

**Step 1: Retrieve FAQ about dental coverage**
```python
faq_chunks = retrieve(query="dental coverage", chunk_type="FAQ")
# Returns: FAQ-005 "Does my plan cover dental?"
```

**Step 2: Retrieve related Rule (via Mapping)**
```python
mapping = retrieve_mapping(question_id="FAQ-005")
# Returns: MAP-005 (FAQ-005 → RULE-003 → PLAN-003)
rule_chunk = retrieve_rule(rule_id="RULE-003")
# Returns: RULE-003 "Benefit Categories and Coverage Types"
```

**Step 3: Check if plan is placeholder**
```python
plan_chunk = retrieve_plan(plan_id="PLAN-003")
# Returns: PLAN-003 "Basic Family Plan" with is_placeholder=true
```

**Step 4: Filter and Answer**
```python
if plan_chunk.is_placeholder == True:
    answer = f"{faq_chunk.text}\n\n{rule_chunk.text}\n\n"
    answer += "⚠️ DISCLAIMER: Dental coverage varies by plan. "
    answer += "Check your policy documents or contact customer service "
    answer += "to confirm whether your Basic Family Plan includes dental benefits."
    # DO NOT state placeholder plan details as fact
else:
    answer = f"{faq_chunk.text}\n\n{rule_chunk.text}\n\n"
    answer += f"For your {plan_chunk.plan_name}: {plan_chunk.dental_coverage_detail}"
    # Safe to provide real plan details
```

**Key Filtering Decision:** Even though PLAN-003 was retrieved, it was NOT used directly because `is_placeholder: true`. Instead, answer defers to policy documents.

---

## 7. Filtering Implementation Patterns

### Pattern 1: Pre-Retrieval Filtering (Recommended)

**Apply filter BEFORE retrieval to reduce search space**

```python
# Customer-facing query
filter_conditions = {
    "is_placeholder": False,
    "status": ["Approved", "Active", "Needs Review", "Pending Detail"],
}

results = vector_db.query(
    query_text="What is a deductible?",
    filter=filter_conditions,
    top_k=10
)
```

**Advantages:**
- Faster (smaller search space)
- Safer (placeholders never retrieved at all)
- Simpler (no post-processing needed)

---

### Pattern 2: Post-Retrieval Filtering (More Flexible)

**Retrieve broadly, filter results after**

```python
# Retrieve all matching chunks
results = vector_db.query(
    query_text="What is a deductible?",
    top_k=20  # Retrieve more to account for filtering
)

# Filter results
filtered_results = [
    r for r in results 
    if not r.metadata.get("is_placeholder", False)
    and r.metadata.get("safe_for_client_direct_use", True)
]

# Re-rank after filtering
top_results = filtered_results[:10]
```

**Advantages:**
- Can inspect what was filtered out (debugging)
- Can apply complex filtering logic
- Can retrieve placeholders for logging/analytics without showing them

**Disadvantages:**
- Slower (retrieve more chunks)
- More complex (post-processing logic)

---

### Pattern 3: Hybrid Filtering (Best of Both)

**Apply strict filters pre-retrieval, flexible filters post-retrieval**

```python
# Pre-retrieval: Hard safety filter
filter_conditions = {
    "is_placeholder": False,  # Never retrieve placeholders for customers
}

results = vector_db.query(
    query_text="What is a deductible?",
    filter=filter_conditions,
    top_k=20
)

# Post-retrieval: Apply use-case specific filtering
if use_case == "customer_chatbot":
    # Prefer Approved/Active, downrank Needs Review
    results = sorted(results, key=lambda r: (
        r.metadata.get("status") in ["Approved", "Active"],
        r.score * r.metadata.get("retrieval_weight_hint", 0.5)
    ), reverse=True)

elif use_case == "internal_assistant":
    # Include all, but label accordingly
    pass  # No additional filtering

top_results = results[:10]
```

---

## 8. Validation Tests for Filtering

### Test 1: Placeholder Leak Detection
**Scenario:** Customer asks "What plans do you offer?"
**Expected:** Answer does NOT list placeholder plans as confirmed products
**Check:** No chunks with `is_placeholder: true` in answer sources

---

### Test 2: Network Verification Requirement
**Scenario:** Customer asks "Is Dubai Medical Center in-network?"
**Expected:** Answer states "Verify provider network status before scheduling"
**Check:** No chunks with `is_placeholder: true` AND `chunk_type: "Network"` used for confirmation

---

### Test 3: Status Filtering
**Scenario:** Query retrieves mix of Approved, Needs Review, Deprecated chunks
**Expected:** Deprecated chunks excluded, Approved ranked highest
**Check:** `status: "Deprecated"` not in results OR clearly labeled as historical

---

### Test 4: Weight Enforcement
**Scenario:** Placeholder has high semantic similarity (0.9), FAQ Approved has medium similarity (0.7)
**Expected:** FAQ Approved (0.7 * 1.0 = 0.7) outranks Placeholder (0.9 * 0.2 = 0.18)
**Check:** Final scores reflect weight application, not just semantic similarity

---

### Test 5: Safe-for-Client Filter
**Scenario:** Retrieve chunks for customer-facing answer
**Expected:** Only chunks with `safe_for_client_direct_use: true` OR clearly disclaimed
**Check:** RULE-008 (Needs Review) and Mapping chunks not directly displayed

---

## 9. Filtering Decision Tree

```
Customer Query Received
│
├─ Use Case?
│  ├─ Customer-Facing
│  │  ├─ Apply Mandatory Filters:
│  │  │  ├─ is_placeholder = false ✓
│  │  │  ├─ status != "Deprecated" ✓
│  │  │  └─ safe_for_client_direct_use = true (preferred) ✓
│  │  ├─ Retrieve with filters
│  │  ├─ Apply retrieval weights
│  │  ├─ Exclude Mapping from direct display
│  │  └─ Generate answer with disclaimers if needed
│  │
│  ├─ Internal Assistant
│  │  ├─ Apply Moderate Filters:
│  │  │  ├─ Include placeholders with warnings ⚠️
│  │  │  ├─ Include Mapping for cross-reference
│  │  │  └─ Show deprecated with labels
│  │  ├─ Retrieve broadly
│  │  └─ Label placeholder status clearly
│  │
│  └─ Self-Service FAQ
│     ├─ Apply Strict Filters:
│     │  ├─ chunk_type = "FAQ" only
│     │  ├─ status = "Approved" only
│     │  └─ confidence = "High" only
│     ├─ Retrieve minimal set
│     └─ Generate simple, high-confidence answer
│
└─ Return filtered results to answer generation
```

---

## 10. Common Filtering Mistakes to Avoid

### Mistake 1: Not Filtering Placeholders
**Problem:** Placeholder plans/network appear in customer answers as confirmed facts
**Fix:** ALWAYS filter `is_placeholder: true` for customer-facing retrieval
**Severity:** CRITICAL - Legal liability

---

### Mistake 2: Ignoring Retrieval Weights
**Problem:** Placeholders with good semantic match outrank FAQ/Rules
**Fix:** Apply retrieval_weight_hint in scoring formula
**Severity:** HIGH - Degrades answer quality

---

### Mistake 3: Displaying Mapping Directly
**Problem:** Mapping text shown to customers (not customer-friendly)
**Fix:** Use Mapping for cross-reference context, not direct display
**Severity:** MEDIUM - Confusing to customers

---

### Mistake 4: Not Downranking Needs Review
**Problem:** RULE-008 (Needs Review) presented without compliance review
**Fix:** Apply status-based filtering/downranking
**Severity:** MEDIUM - Compliance risk

---

### Mistake 5: Filtering Too Strictly (Underutilization)
**Problem:** Filtering out useful FAQ Pending Detail or Needs Review content
**Fix:** Use disclaimers instead of complete exclusion when appropriate
**Severity:** LOW - Reduces system value

---

## 11. Monitoring and Alerting

### Metric 1: Placeholder Leak Rate
**Definition:** % of customer answers that cite placeholder chunks
**Target:** 0%
**Alert:** Any detection of placeholder in customer answer sources
**Action:** Immediate investigation and answer correction

---

### Metric 2: Retrieval Weight Distribution
**Definition:** Distribution of final scores by chunk type (FAQ vs Rules vs Mapping vs Placeholder)
**Target:** FAQ/Rules dominate (>70% of top-10 results)
**Alert:** If placeholders appear in top-10 for customer queries
**Action:** Review weight configuration

---

### Metric 3: Filter Effectiveness
**Definition:** % of chunks removed by filtering before answer generation
**Target:** Depends on use case (customer: 20-30%, internal: 5-10%)
**Alert:** Sudden changes in filter rate
**Action:** Investigate if content changed or filters misconfigured

---

## 12. Document Control

**Filename:** CHUNK_FILTERING_RULES.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Implementation  

**Related Documents:**
- METADATA_APPLICATION_SPEC.md - Metadata fields used for filtering
- RETRIEVAL_WEIGHTING_SPEC.md - Weight enforcement
- PLACEHOLDER_ENFORCEMENT_SPEC.md - Placeholder-specific rules

---

**END OF CHUNK FILTERING RULES SPECIFICATION**

Apply these filtering rules to ensure safe, relevant, customer-appropriate retrieval.
