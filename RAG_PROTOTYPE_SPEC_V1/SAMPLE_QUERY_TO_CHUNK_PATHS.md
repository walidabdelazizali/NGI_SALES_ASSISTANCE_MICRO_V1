# Sample Query-to-Chunk Paths (Worked Examples)

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Reference)  

---

## Purpose

This optional reference document provides **worked examples showing the complete path from query to answer** for the Phase 1 RAG prototype. Each example demonstrates:
- Query input
- Primary chunks retrieved
- Secondary chunks retrieved
- Answer behavior and structure
- Caution behavior (disclaimers, warnings)
- Final answer text

These examples help implementation teams, testers, and future maintainers understand **how the prototype should behave** in practice.

---

## Example 1: Clean Conceptual Query (Tier 1)

### Query
```
"What is a deductible?"
```

### Query Classification
- **Query Type:** Conceptual (Type 1)
- **Intent:** Insurance term definition
- **Entities Extracted:** ["deductible"]
- **Plan Mentioned:** No
- **Network Mentioned:** No

### Retrieval Results

#### Primary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|-------------|-----------------|
| 1 | FAQ-001 | FAQ | Approved | 0.92 | 1.0 | **0.92** | TRUE |
| 2 | RULE-001 | Rules | Active | 0.85 | 0.9 | **0.77** | TRUE |
| 3 | FAQ-004 | FAQ | Approved | 0.78 | 1.0 | **0.78** | TRUE |

#### Secondary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|-------------|-----------------|
| 4 | MAP-005 | Mapping | - | 0.65 | 0.5 | **0.33** | FALSE (context) |

#### Placeholder Chunks Retrieved
None (conceptual query, no plan/network context)

### Source Assembly

**Chunks Used for Answer:**
- FAQ-001 (primary) - Deductible definition
- RULE-001 (secondary) - Cost-sharing logic for context
- FAQ-004 (tertiary) - Deductible examples

**Chunks Used for Context Only:**
- MAP-005 - Cross-reference to coinsurance, copay, OOP max (not displayed directly)

### Confidence Tier Calculation

```
has_faq = True (FAQ-001, FAQ-004)
has_rules = True (RULE-001)
has_placeholder = False
max_semantic_score = 0.92 (high)

→ Tier 1 (Strongest): FAQ + Rules, no placeholders, high semantic match
```

### Disclaimers Applied

**Mandatory Situations Checked:**
1. Plan confirmation required? → No (no plan mentioned)
2. Network verification required? → No (no network keywords)
3. Placeholder present? → No
4. Low confidence? → No (max score 0.92)
5. Compliance/legal topic? → No
6. Operational pending? → No

**Disclaimers Applied:** None

### Answer Generated

**Answer Structure:**
1. Direct answer (from FAQ-001)
2. Supporting detail with example (from FAQ-004)
3. Policy reasoning (from RULE-001)

**Final Answer:**
```
A deductible is the amount you pay out-of-pocket for covered healthcare services 
before your insurance plan begins to pay. 

For example, if your deductible is $1,000, you pay the first $1,000 of covered 
services yourself. Once you meet your deductible, your insurance starts covering 
a portion of costs, though you may still have copays or coinsurance depending on 
your plan.

The deductible is part of your plan's cost-sharing structure, which helps balance 
premium costs with out-of-pocket expenses. Some preventive care services may be 
covered before you meet your deductible.
```

### Metadata Logged

```json
{
  "query_metadata": {
    "query_text": "What is a deductible?",
    "query_classification": "Conceptual",
    "intent": "term_definition",
    "entities_extracted": ["deductible"]
  },
  "source_metadata": [
    {"chunk_id": "FAQ-001", "chunk_type": "FAQ", "score": 0.92, "rank": 1},
    {"chunk_id": "RULE-001", "chunk_type": "Rules", "score": 0.77, "rank": 2},
    {"chunk_id": "FAQ-004", "chunk_type": "FAQ", "score": 0.78, "rank": 3},
    {"chunk_id": "MAP-005", "chunk_type": "Mapping", "score": 0.33, "rank": 4}
  ],
  "answer_metadata": {
    "overall_confidence_tier": "Tier 1",
    "weakest_source": "None (all strengths: High)",
    "disclaimers_applied": [],
    "safety_rules_triggered": [],
    "exclusions_checked": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "violations_detected": []
  }
}
```

---

## Example 2: Plan-Specific Query with Placeholder (Tier 3)

### Query
```
"Does the Basic Family Plan cover dental?"
```

### Query Classification
- **Query Type:** Plan-Specific (Type 3)
- **Intent:** Plan benefit inquiry
- **Entities Extracted:** ["Basic Family Plan", "dental"]
- **Plan Mentioned:** Yes (Basic Family Plan)
- **Network Mentioned:** No

### Retrieval Results

#### Primary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|-------------|-----------------|
| 1 | FAQ-005 | FAQ | Approved | 0.88 | 1.0 | **0.88** | TRUE |
| 2 | RULE-003 | Rules | Active | 0.82 | 0.9 | **0.74** | TRUE |

#### Secondary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|-------------|-----------------|
| 3 | MAP-008 | Mapping | - | 0.70 | 0.5 | **0.35** | FALSE (context) |

#### Placeholder Chunks Retrieved (Downweighted)
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Penalty | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|---------|-------------|-----------------|
| 8 | PLAN-003 | Plans | Pending Detail | 0.75 | 0.2 | ×0.08 | **0.012** | FALSE |

**Note:** PLAN-003 is "Basic Family Plan" placeholder. High semantic match (0.75) BUT heavily downweighted: 0.75 × 0.2 × 0.08 = **0.012 (score < 0.1)**

### Source Assembly

**Chunks Used for Answer:**
- FAQ-005 (primary) - General dental coverage explanation
- RULE-003 (secondary) - Benefit categories logic

**Chunks Used for Context Only:**
- PLAN-003 - Recognizes "Basic Family Plan" name, but details NOT used
- MAP-008 - Cross-reference to dental benefit categories (not displayed)

### Confidence Tier Calculation

```
has_faq = True (FAQ-005)
has_rules = True (RULE-003)
has_placeholder = True (PLAN-003)  ← KEY FACTOR
max_semantic_score = 0.88 (high)

→ Tier 3 (Moderate): Placeholder present triggers downgrade, even though FAQ+Rules available and high semantic match
```

**Weakest Link Rule Applied:** PLAN-003 placeholder downgrades overall confidence from Tier 1 to Tier 3

### Disclaimers Applied

**Mandatory Situations Checked:**
1. Plan confirmation required? → **Yes** (plan name "Basic Family Plan" mentioned)
2. Network verification required? → No
3. Placeholder present? → **Yes** (PLAN-003)
4. Low confidence? → No (max score 0.88 for FAQ/Rules, but Tier 3 due to placeholder)
5. Compliance/legal topic? → No
6. Operational pending? → No

**Disclaimers Applied:**
- ✅ "Coverage details vary by plan. Check your policy documents or contact customer service."

### Answer Generated

**Answer Structure:**
1. General dental coverage guidance (from FAQ-005)
2. Benefit categories explanation (from RULE-003)
3. Plan name recognition (from PLAN-003 context)
4. **Verification steps (mandatory for plan-specific)**
5. **Disclaimer (mandatory)**

**Final Answer:**
```
Dental coverage varies by plan type and tier. Many plans include preventive 
dental care such as routine cleanings, exams, and X-rays. Some plans also include 
coverage for basic procedures (fillings, extractions) and major procedures (crowns, 
bridges, root canals).

Dental benefits are typically organized into categories:
- Preventive care: Usually covered at a higher percentage (often 80-100%)
- Basic procedures: Moderate coverage (often 60-80%)
- Major procedures: Lower coverage (often 50-60%)

For your Basic Family Plan's specific dental coverage details, please:
- Check your policy documents or benefits summary (Section: Dental Benefits)
- Contact customer service at [phone number]
- Log into your member portal and review plan benefits

**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service for your specific plan's dental benefits.
```

### What Answer Does NOT Say (Critical)

**Prohibited (from PLAN-003 placeholder):**
- ❌ "Yes, the Basic Family Plan covers dental."
- ❌ "Basic Family Plan covers dental with 80% coinsurance for preventive care."
- ❌ "Basic Family Plan does not include orthodontics."

**Why Prohibited:** PLAN-003 has `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`. Stating placeholder details as facts = CRITICAL violation (Exclusion 1).

**Allowed:**
- ✅ Recognizes plan name "Basic Family Plan" for context
- ✅ Provides general dental coverage guidance from FAQ/Rules
- ✅ Directs to verification sources (policy documents, customer service)
- ✅ Adds mandatory disclaimer

### Metadata Logged

```json
{
  "query_metadata": {
    "query_text": "Does the Basic Family Plan cover dental?",
    "query_classification": "Plan-Specific",
    "intent": "plan_benefit_inquiry",
    "entities_extracted": ["Basic Family Plan", "dental"]
  },
  "source_metadata": [
    {"chunk_id": "FAQ-005", "chunk_type": "FAQ", "status": "Approved", "score": 0.88, "rank": 1},
    {"chunk_id": "RULE-003", "chunk_type": "Rules", "status": "Active", "score": 0.74, "rank": 2},
    {"chunk_id": "MAP-008", "chunk_type": "Mapping", "score": 0.35, "rank": 3},
    {"chunk_id": "PLAN-003", "chunk_type": "Plans", "status": "Pending Detail", 
     "score_before_penalty": 0.75, "penalty": 0.08, "score_after_penalty": 0.012, 
     "rank": 8, "is_placeholder": true, "safe_for_client_direct_use": false}
  ],
  "answer_metadata": {
    "overall_confidence_tier": "Tier 3",
    "weakest_source": {
      "chunk_id": "PLAN-003",
      "reason": "Placeholder chunk present, confidence downgraded"
    },
    "disclaimers_applied": [
      "Coverage details vary by plan. Check your policy documents or contact customer service."
    ],
    "safety_rules_triggered": [
      "plan_confirmation_required",
      "placeholder_present"
    ],
    "exclusions_checked": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "violations_detected": []
  }
}
```

---

## Example 3: Network-Specific Query with Placeholder (Tier 3)

### Query
```
"Is Dr. Ahmed in-network?"
```

### Query Classification
- **Query Type:** Network-Specific (Type 4)
- **Intent:** Provider network status inquiry
- **Entities Extracted:** ["Dr. Ahmed"]
- **Plan Mentioned:** No
- **Network Mentioned:** Yes (in-network keyword, provider name)

### Retrieval Results

#### Primary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|-------------|-----------------|
| 1 | FAQ-015 | FAQ | Approved | 0.90 | 1.0 | **0.90** | TRUE |
| 2 | RULE-012 | Rules | Active | 0.83 | 0.9 | **0.75** | TRUE |

#### Placeholder Chunks Retrieved (Downweighted)
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Penalty | Final Score | Safe for Client |
|------|----------|------------|--------|----------------|------------------|---------|-------------|-----------------|
| 7 | PROV-002 | Network | Pending Detail | 0.80 | 0.2 | ×0.08 | **0.013** | FALSE |

**Note:** PROV-002 is "Dr. Ahmed Al-Mansoori, Internal Medicine" placeholder. High semantic match BUT heavily downweighted: 0.80 × 0.2 × 0.08 = **0.013 (score < 0.1)**

### Source Assembly

**Chunks Used for Answer:**
- FAQ-015 (primary) - Network verification process
- RULE-012 (secondary) - In-network vs out-of-network policies

**Chunks Used for Context Only:**
- PROV-002 - Recognizes "Dr. Ahmed" provider name, but network status NOT confirmed

### Confidence Tier Calculation

```
has_faq = True (FAQ-015)
has_rules = True (RULE-012)
has_placeholder = True (PROV-002)  ← KEY FACTOR
max_semantic_score = 0.90 (high)

→ Tier 3 (Moderate): Placeholder present triggers downgrade
```

### Disclaimers Applied

**Mandatory Situations Checked:**
1. Plan confirmation required? → No
2. Network verification required? → **Yes** (network keywords + Network chunk retrieved)
3. Placeholder present? → **Yes** (PROV-002)
4. Low confidence? → No
5. Compliance/legal topic? → No
6. Operational pending? → No

**Disclaimers Applied:**
- ✅ "Provider network status may vary. Always verify with customer service before scheduling your appointment."

### Answer Generated

**Answer Structure:**
1. Network verification process (from FAQ-015)
2. In-network vs out-of-network explanation (from RULE-012)
3. Provider name recognition (from PROV-002 context)
4. **Verification steps (mandatory for network queries)**
5. **Disclaimer (mandatory)**

**Final Answer:**
```
To verify if a provider is in your network, you can:

1. **Call customer service** at [phone number] with the provider's name, specialty, 
   and location
2. **Log into your member portal** and use the provider directory search
3. **Ask the provider's office** to verify your insurance coverage before your 
   appointment

In-network providers have contracted rates with the insurance company, resulting 
in lower out-of-pocket costs for you. Out-of-network providers may charge higher 
rates, and you may be responsible for the difference.

When seeking care, especially for planned procedures or ongoing treatment, it's 
important to verify network status to avoid unexpected costs.

**Important:** Provider network status can change. Always verify before scheduling 
your appointment to avoid unexpected costs.
```

### What Answer Does NOT Say (Critical)

**Prohibited (from PROV-002 placeholder):**
- ❌ "Yes, Dr. Ahmed is in-network."
- ❌ "Dr. Ahmed accepts Basic Family Plan."
- ❌ "Dr. Ahmed is contracted with our network."

**Why Prohibited:** PROV-002 has `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`. Confirming network status from placeholder = CRITICAL violation (Exclusion 2).

**Allowed:**
- ✅ Recognizes "Dr. Ahmed" for context (user asking about specific provider)
- ✅ Provides general network verification process
- ✅ Explains in-network vs out-of-network
- ✅ Directs to verification sources
- ✅ Adds mandatory network verification disclaimer

### Metadata Logged

```json
{
  "query_metadata": {
    "query_text": "Is Dr. Ahmed in-network?",
    "query_classification": "Network-Specific",
    "intent": "network_status_inquiry",
    "entities_extracted": ["Dr. Ahmed", "in-network"]
  },
  "source_metadata": [
    {"chunk_id": "FAQ-015", "chunk_type": "FAQ", "status": "Approved", "score": 0.90, "rank": 1},
    {"chunk_id": "RULE-012", "chunk_type": "Rules", "status": "Active", "score": 0.75, "rank": 2},
    {"chunk_id": "PROV-002", "chunk_type": "Network", "status": "Pending Detail",
     "score_before_penalty": 0.80, "penalty": 0.08, "score_after_penalty": 0.013,
     "rank": 7, "is_placeholder": true, "safe_for_client_direct_use": false}
  ],
  "answer_metadata": {
    "overall_confidence_tier": "Tier 3",
    "weakest_source": {
      "chunk_id": "PROV-002",
      "reason": "Network placeholder present, confidence downgraded"
    },
    "disclaimers_applied": [
      "Provider network status may vary. Always verify before scheduling appointment."
    ],
    "safety_rules_triggered": [
      "network_verification_required",
      "placeholder_present"
    ],
    "exclusions_checked": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "violations_detected": []
  }
}
```

---

## Example 4: Mixed Query (Plan + Network + Benefit) (Tier 3)

### Query
```
"Does my Basic Family Plan cover Dr. Ahmed for maternity services?"
```

### Query Classification
- **Query Type:** Mixed (Type 6) - Plan + Network + Benefit
- **Intent:** Multiple (plan_benefit + network_status + coverage_inquiry)
- **Entities Extracted:** ["Basic Family Plan", "Dr. Ahmed", "maternity services"]
- **Plan Mentioned:** Yes
- **Network Mentioned:** Yes

### Retrieval Results

#### Primary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Retrieval Weight | Final Score |
|------|----------|------------|--------|----------------|------------------|-------------|
| 1 | FAQ-007 | FAQ | Approved | 0.89 | 1.0 | **0.89** |
| 2 | FAQ-015 | FAQ | Approved | 0.82 | 1.0 | **0.82** |
| 3 | RULE-009 | Rules | Active | 0.85 | 0.9 | **0.77** |

#### Placeholder Chunks Retrieved (Downweighted)
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Penalty | Final Score |
|------|----------|------------|--------|----------------|---------|-------------|
| 6 | PLAN-003 | Plans | Pending Detail | 0.78 | ×0.08 | **0.012** |
| 8 | PROV-002 | Network | Pending Detail | 0.74 | ×0.08 | **0.012** |

### Source Assembly
- FAQ-007 (maternity coverage general)
- FAQ-015 (network verification)
- RULE-009 (maternity rules)
- PLAN-003 (recognizes "Basic Family Plan", context only)
- PROV-002 (recognizes "Dr. Ahmed", context only)

### Confidence Tier
**Tier 3** (placeholders present: PLAN-003 + PROV-002)

### Disclaimers Applied
- ✅ Plan confirmation: "Coverage details vary by plan. Check your policy documents."
- ✅ Network verification: "Provider network status may vary. Verify before appointment."

### Answer Generated

**Final Answer:**
```
Maternity coverage typically includes prenatal care, delivery, and postnatal care. 
Most insurance plans cover maternity services, but coverage details (copays, 
deductibles, hospital stay limits, specialist visits) vary by plan tier.

**For your Basic Family Plan's specific maternity coverage:**
- Check your policy documents (Section: Maternity Benefits)
- Contact customer service at [phone number]
- Review benefits summary for copays and deductibles

**To verify if Dr. Ahmed provides maternity services in your network:**
- Call customer service with Dr. Ahmed's name, specialty, and location
- Use the member portal provider directory
- Ask Dr. Ahmed's office to verify your insurance coverage

**Important:**
- Coverage details vary by plan. Check your policy documents or contact customer service.
- Provider network status may vary. Always verify before scheduling your appointment.
```

### What Answer Does NOT Say
- ❌ "Yes, Basic Family Plan covers maternity services."
- ❌ "Dr. Ahmed is in-network for maternity care."
- ❌ "Your maternity copay is $50 per visit."

**Why:** All would state placeholder details as facts (CRITICAL violations).

---

## Example 5: Unsupported Query (Account-Specific) (Tier 5)

### Query
```
"What's my current claim status?"
```

### Query Classification
- **Query Type:** Unsupported/Account (Type 7)
- **Intent:** Account-specific data request
- **Entities Extracted:** ["claim status"]
- **Account-Specific:** Yes

### Retrieval Results

#### Primary Chunks Retrieved
| Rank | Chunk ID | Chunk Type | Status | Semantic Score | Final Score |
|------|----------|------------|--------|----------------|-------------|
| 1 | FAQ-009 | FAQ | Approved | 0.65 | **0.65** |
| 2 | RULE-015 | Rules | Active | 0.58 | **0.52** |

**Note:** FAQ-009 is "How to file a claim" (process guidance), NOT account-specific claim status.

### Source Assembly
- FAQ-009 retrieved but provides general claims process, NOT account-specific status
- No chunks provide actual claim status (requires account system integration)

### Confidence Tier
**Tier 5 (Unsafe)** - Account-specific query, no reliable sources for personalized data

### Disclaimers Applied
- ✅ Account-specific fallback: "For account-specific information, contact customer service or log into member portal."

### Answer Generated

**Final Answer:**
```
For account-specific information like claim status, deductible balance, or member 
ID, please:

- **Log into your member portal** at [portal URL] to view real-time claim status
- **Contact customer service** at [phone number] for personalized assistance
- **Review your Explanation of Benefits (EOB)** mailed after claim processing

Customer service representatives have access to your account details and can 
provide personalized assistance with your claim status, payment information, 
and next steps.

If you need general information about the claims process, I can help with that.
```

### What Answer Does NOT Attempt
- ❌ Does NOT attempt to provide claim status from weak sources
- ❌ Does NOT make up claim information
- ❌ Does NOT attempt account operations

**Why:** Account-specific queries are out of scope (no system integration). Safe fallback directs to appropriate resources.

---

## Summary: Key Patterns

### Pattern 1: Tier 1 (Clean FAQ/Rules)
- **Retrieval:** FAQ + Rules, high semantic match, NO placeholders
- **Answer:** Direct, confident, customer-friendly language from FAQ
- **Disclaimers:** None (or minimal)
- **Example:** "What is a deductible?"

### Pattern 2: Tier 3 (Placeholders Present)
- **Retrieval:** FAQ + Rules (strong) + Plans/Network placeholders (downweighted <0.1)
- **Answer:** General guidance from FAQ/Rules, recognizes plan/provider names, directs to verification
- **Disclaimers:** MANDATORY (plan confirmation OR network verification)
- **What NOT to do:** NEVER state placeholder details as facts
- **Example:** "Does Basic Family Plan cover dental?", "Is Dr. Ahmed in-network?"

### Pattern 3: Tier 5 (No Reliable Sources)
- **Retrieval:** Low semantic match OR account-specific OR off-topic
- **Answer:** Safe fallback, directs to appropriate resources
- **Disclaimers:** Account-specific or general fallback
- **What NOT to do:** NEVER attempt answer from weak sources
- **Example:** "What's my claim status?", "What's the weather?"

---

## Document Control

**Filename:** SAMPLE_QUERY_TO_CHUNK_PATHS.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Reference)  

**Related Documents:**
- PROTOTYPE_RETRIEVAL_FLOW.md - Retrieval process details
- PROTOTYPE_QUERY_HANDLING.md - Query type strategies
- PROTOTYPE_RESPONSE_BEHAVIOR.md - Answer generation rules
- PROTOTYPE_EXCLUSIONS.md - What not to do
- PROTOTYPE_TEST_QUERIES.md - Full test query set

---

**END OF WORKED EXAMPLES**
