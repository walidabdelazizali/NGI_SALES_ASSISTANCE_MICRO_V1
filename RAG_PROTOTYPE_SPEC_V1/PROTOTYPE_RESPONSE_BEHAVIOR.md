# Prototype Response Behavior Specification

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document defines **how the internal RAG prototype should generate and format answers**, specifying answer style, traceability requirements, disclaimer behavior, and safety rules to prevent placeholder content from creating false certainty.

---

## Core Response Principles

### 1. Truth Over Completeness

**Principle:** It is better to provide an incomplete but truthful answer than a complete but uncertain answer.

**Application:**
- If only FAQ/Rules available → provide confident answer to what is known
- If placeholders required for completeness → acknowledge limitation, provide general guidance, add strong disclaimer
- If no reliable sources → refuse to answer with certainty, provide safe fallback

**Example:**
```
Query: "Does the Basic Family Plan cover dental implants?"

Weak Response (completeness-focused):
❌ "The Basic Family Plan covers dental implants with 50% coinsurance."
(States placeholder details as fact)

Strong Response (truth-focused):
✅ "Dental coverage varies by plan type and tier. Many plans include 
preventive dental care, and some include coverage for major procedures 
like implants. For your Basic Family Plan's specific dental implant 
coverage, please check your policy documents or contact customer service."
(Provides true general guidance, acknowledges limitation, directs to verification)
```

---

### 2. Customer-Friendly Language from FAQ

**Principle:** Use FAQ wording as the primary language for customer communication because FAQ chunks are written for customer understanding.

**Application:**
- Quote or paraphrase FAQ content directly when possible
- Avoid technical policy language from Rules unless necessary
- Simplify complex Rules reasoning using FAQ-style language
- Provide examples when FAQ includes them

**Example:**
```
Rules content: "Deductible mechanism operates as prerequisite cost-sharing 
obligation prior to benefit disbursement initiation."

FAQ content: "A deductible is the amount you pay out-of-pocket before your 
insurance plan begins to pay."

Response should use FAQ language:
✅ "A deductible is the amount you pay out-of-pocket before your insurance 
plan begins to pay."
```

---

### 3. Rules for Logic and Reasoning

**Principle:** Use Rules chunks to provide policy reasoning, benefit logic, and "why" explanations.

**Application:**
- When FAQ provides "what" → Rules provide "why"
- When multiple benefits interact → Rules explain the logic
- When exceptions exist → Rules clarify the conditions

**Example:**
```
Query: "Why do I need pre-authorization for specialists?"

FAQ provides: "Some specialist visits require pre-authorization."

Rules provides: "Pre-authorization ensures medical necessity and appropriate 
care pathway before specialist referral."

Response combines both:
✅ "Some specialist visits require pre-authorization to ensure the care is 
medically necessary and follows the appropriate treatment pathway. This helps 
control costs and ensure quality care. Check with customer service before 
scheduling specialist appointments to confirm if pre-authorization is needed."
```

---

### 4. Mapping for Cross-Linking (Never Display Directly)

**Principle:** Use Mapping chunks to discover related FAQ/Rules and provide context, but NEVER display Mapping content directly to users.

**Application:**
- Mapping identifies related topics → retrieve those topics and display them
- Mapping links FAQ to Rules → use to enrich answer
- Mapping suggests next questions → mention related topics

**Example:**
```
Query: "What is a deductible?"

Mapping identifies: FAQ-001 (deductible) links to FAQ-002 (copay), FAQ-003 (coinsurance)

Response uses Mapping for cross-reference:
✅ "A deductible is the amount you pay out-of-pocket before your insurance plan 
begins to pay. [Full explanation from FAQ-001]

Related concepts: copay, coinsurance, out-of-pocket maximum"
(Mapping used to identify related topics, but Mapping text NOT displayed)
```

---

### 5. Honest About Limitations

**Principle:** Be transparent when the prototype lacks sufficient information or when real-world verification is required.

**Application:**
- If FAQ status = "Pending Detail" → acknowledge incomplete information
- If only placeholders available → refuse to answer from placeholders, provide safe fallback
- If real-time data needed (network status, claim status) → direct to appropriate channel
- If out of KB scope → be honest, don't attempt weak answer

**Example:**
```
Query: "How do I refill a prescription?"

FAQ-011 status = "Pending Detail" (incomplete)

Response is honest:
✅ "To refill a prescription, you can typically use your pharmacy's online refill 
system, call the pharmacy directly, or visit in person. For detailed instructions 
specific to your insurance plan and pharmacy network, please contact customer 
service at [number].

**Note:** Contact customer service for step-by-step instructions specific to your situation."
```

---

### 6. Placeholders Must Not Create False Certainty

**Principle:** Placeholder Plans and Network chunks are structural scaffolding only, NOT confirmed product/provider data. They must NEVER be presented as authoritative facts.

**Critical Rules:**
- ❌ **NEVER state placeholder plan benefits as confirmed facts**
- ❌ **NEVER confirm provider network status from placeholders**
- ❌ **NEVER state placeholder costs/copays/deductibles as facts**
- ✅ **DO recognize plan/provider names from placeholders (context awareness)**
- ✅ **DO provide general guidance from FAQ/Rules**
- ✅ **DO add mandatory disclaimers when placeholders present**

**Example:**
```
Query: "What's the copay for the Basic Family Plan?"

Retrieved: PLAN-003 (Basic Family Plan placeholder with copay=$30)

Wrong Response:
❌ "The copay for the Basic Family Plan is $30."
(States placeholder detail as confirmed fact)

Correct Response:
✅ "Copay amounts vary by plan type and service category. Most plans have copays 
ranging from $20-$75 depending on the type of provider (primary care vs specialist) 
and plan tier.

For your Basic Family Plan's specific copay amounts, please:
- Check your policy documents (Section: Cost Sharing)
- Contact customer service at [number]
- Log into your member portal

**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service."
(Provides general truth from FAQ/Rules, recognizes plan name, adds strong disclaimer)
```

---

## Answer Structure Template

All prototype answers should follow this structure:

```
[1. Direct Answer - from FAQ/Rules]
[Primary information addressing the query]

[2. Supporting Detail - from Rules/FAQ]
[Additional context, reasoning, or examples]

[3. Related Information - from Mapping] (optional)
[Cross-references to related topics]

[4. Verification Steps] (if plan/network-specific)
[How to verify plan-specific or network-specific details]

[5. Disclaimers] (based on confidence tier and query type)
[Required disclaimers for plan confirmation, network verification, etc.]

[6. Contact Information] (if needed)
[How to get personalized assistance]
```

---

## Answer Examples by Confidence Tier

### Tier 1: Strongest (FAQ + Rules only, no placeholders)

**Query:** "What is a deductible?"

**Retrieved Sources:**
- FAQ-001 (deductible definition, High confidence, Approved)
- RULE-001 (cost-sharing logic, Active)

**Answer:**
```
A deductible is the amount you pay out-of-pocket for covered healthcare services 
before your insurance plan begins to pay. For example, if your deductible is $1,000, 
you pay the first $1,000 of covered services yourself.

Once you meet your deductible, your insurance starts covering a portion of costs, 
though you may still have copays or coinsurance depending on your plan. The 
deductible resets annually at the start of your plan year.

Related concepts: copay, coinsurance, out-of-pocket maximum

[No disclaimers needed - high confidence answer]
```

**Characteristics:**
- ✅ Direct, confident answer
- ✅ Uses FAQ language
- ✅ Provides examples
- ✅ Cross-references related topics
- ✅ No disclaimers (not needed)
- ✅ No placeholders involved

---

### Tier 2: Strong (FAQ + Rules + Mapping, no placeholders)

**Query:** "What's the difference between in-network and out-of-network?"

**Retrieved Sources:**
- FAQ-015 (network differences, High confidence, Approved)
- RULE-012 (network policies, Active)
- MAP-015 (links network to billing/reimbursement)

**Answer:**
```
In-network providers have contracted rates with the insurance company, resulting 
in lower out-of-pocket costs. Out-of-network providers do not have contracted 
rates and may charge higher amounts, which could result in higher costs for you.

When you use in-network providers:
- You typically pay lower copays or coinsurance
- The provider bills the insurance directly
- Services are covered according to your plan's benefit schedule

When you use out-of-network providers:
- You may pay higher coinsurance or full charges
- You may need to pay upfront and file for reimbursement
- Some services may not be covered at all

Always verify a provider's network status before receiving services to avoid 
unexpected costs.

Related topics: direct billing, reimbursement process, provider directories

[Minimal disclaimers - strong answer with cross-references]
```

**Characteristics:**
- ✅ Confident answer with detail
- ✅ Uses FAQ + Rules for comprehensive explanation
- ✅ Mapping used to identify related topics (billing, reimbursement)
- ✅ Provides actionable guidance
- ✅ Minimal disclaimers

---

### Tier 3: Moderate (FAQ + Rules + Placeholders present)

**Query:** "Does the Basic Family Plan cover dental?"

**Retrieved Sources:**
- FAQ-005 (dental coverage general, High confidence, Approved)
- RULE-003 (benefit categories, Active)
- PLAN-003 (Basic Family Plan placeholder, Low confidence, Pending Detail)

**Answer:**
```
Dental coverage varies by plan type and tier. Many plans include preventive 
dental care (cleanings, exams), and some plans include additional coverage for 
basic procedures (fillings) and major procedures (crowns, bridges).

Coverage typically includes:
- Preventive care: 100% coverage (no copay)
- Basic procedures: 70-80% coverage after deductible
- Major procedures: 50% coverage after deductible

For your Basic Family Plan's specific dental coverage details, please:
- Check your policy documents or benefits summary
- Contact customer service at [number]
- Log into your member portal and review plan benefits

**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service.
```

**Characteristics:**
- ✅ Provides general guidance from FAQ/Rules (true information)
- ✅ Recognizes "Basic Family Plan" from placeholder (context awareness)
- ❌ Does NOT state placeholder details as facts
- ✅ **Mandatory disclaimer** about plan confirmation
- ✅ Provides verification steps
- ✅ Placeholder present but NOT trusted

---

### Tier 4: Weak (Rules only, no FAQ)

**Query:** "What happens if I don't disclose pre-existing conditions?"

**Retrieved Sources:**
- RULE-008 (disclosure requirements, status = Needs Review)
- No FAQ chunks retrieved (coverage gap)

**Answer:**
```
Policy generally requires full disclosure of pre-existing conditions during 
enrollment. Failure to disclose may result in claim denials or policy complications.

For personalized guidance about pre-existing condition disclosure requirements 
and potential consequences:
- Consult your policy documents (Section: Enrollment Requirements)
- Contact customer service at [number]
- Speak with your HR benefits coordinator

**Note:** This is a compliance matter. For personalized guidance, contact customer 
service or your benefits coordinator.
```

**Characteristics:**
- ⚠️ Provides policy reasoning from Rules
- ⚠️ Acknowledges limited FAQ coverage
- ✅ Strong disclaimer about compliance matter
- ✅ Directs to appropriate contacts
- ⚠️ Moderate confidence (Rules-only answer)

---

### Tier 5: Unsafe (Placeholders only, no FAQ/Rules)

**Query:** "What are the specific benefits of the Economy Starter Plan?"

**Retrieved Sources:**
- PLAN-007 (Economy Starter Plan placeholder, Low confidence, Pending Detail)
- No FAQ or Rules chunks retrieved (semantic match < 0.5)

**Answer:**
```
I don't have reliable information about specific plan benefits at this time. 

For accurate information about plan options and benefits, please:
- Contact customer service at [number]
- Visit our website at [url]
- Schedule a consultation with a benefits advisor
- Review plan comparison documents provided during enrollment

Customer service representatives can provide detailed information about all 
available plans and help you choose the right coverage for your needs.
```

**Characteristics:**
- ❌ Refuses to answer from placeholder alone
- ✅ Provides safe fallback response
- ✅ Directs to appropriate contact channels
- ✅ Honest about limitation
- ✅ **Critical safety behavior:** Does not attempt answer from weak sources

---

## Disclaimer Application Rules

### When to Add Disclaimers

Disclaimers are **mandatory** in these situations:

**1. Plan Confirmation Required (`requires_plan_confirmation = TRUE`)**

Trigger:
- Any plan-specific query
- Any query where plan tier/type affects answer
- Any cost/pricing question

Disclaimer:
```
**Note:** Coverage details vary by plan. Check your policy documents or contact 
customer service.
```

---

**2. Network Verification Required (`requires_network_verification = TRUE`)**

Trigger:
- Any network-specific query
- Any query about specific provider/facility
- Any query about in-network vs out-of-network

Disclaimer:
```
**Important:** Provider network status may vary. Verify with customer service 
before scheduling appointment.
```

---

**3. Operational Process Pending Detail (FAQ status = "Pending Detail")**

Trigger:
- FAQ status = "Pending Detail"
- Operational process question with incomplete details

Disclaimer:
```
**Note:** Contact customer service at [number] for step-by-step instructions 
specific to your situation.
```

---

**4. Placeholder Present (any placeholder in retrieved sources)**

Trigger:
- Any Plans placeholder retrieved
- Any Network placeholder retrieved
- Confidence tier = Tier 3 or lower due to placeholder

Disclaimer:
```
**Note:** For specific details about your plan or provider, verify with customer 
service.
```

---

**5. Low Confidence (overall confidence = Low or Very Low)**

Trigger:
- Semantic match < 0.6
- Status = "Needs Review" or "Pending Detail"
- Rules-only answer (no FAQ)

Disclaimer:
```
**Note:** I have limited information on this topic. For accurate details, contact 
customer service at [number].
```

---

**6. Compliance/Legal Matter (Rules status = "Needs Review" + compliance topic)**

Trigger:
- Query about disclosure, pre-existing conditions, fraud, compliance
- Rules status = "Needs Review"

Disclaimer:
```
**Note:** This is a compliance matter. For personalized guidance, consult your 
policy documents or contact the compliance team.
```

---

### When NOT to Add Disclaimers

Disclaaimers are **not needed** for:
- Tier 1 queries (FAQ + Rules only, no placeholders)
- Conceptual questions with high-confidence answer
- General insurance definitions
- Process explanations with Approved status

**Example of Clean Answer (No disclaimers needed):**
```
Query: "What is a copay?"

Answer: "A copay is a fixed amount you pay for a covered healthcare service, 
usually at the time of service. For example, you might pay a $25 copay when 
you visit your primary care doctor. Copays vary by plan and service type."

[No disclaimer needed - high confidence conceptual answer]
```

---

## Traceability Requirements

Every prototype answer **must** include internal traceability metadata (not shown to end user, but available for testing/debugging).

### Required Traceability Fields

For each answer, capture:

**Query Metadata:**
- `query_original`: Original query text
- `query_normalized`: Normalized query text
- `query_intent`: Detected intent category
- `query_timestamp`: When query was processed

**Source Metadata:**
For each source chunk used:
- `chunk_id`: Unique chunk identifier (e.g., FAQ-001)
- `source_file`: Source JSONL file (e.g., faq_chunks.jsonl)
- `source_chunk_id`: Original chunk ID from KB_PACK_V1
- `chunk_type`: FAQ, Rules, Mapping, Plans, Network
- `retrieval_score`: Semantic similarity score (0.0-1.0)
- `confidence`: High, Medium, Low, Very Low
- `status`: Approved, Active, Needs Review, Pending Detail, Deprecated
- `is_placeholder`: TRUE/FALSE
- `safe_for_client_direct_use`: TRUE/FALSE
- `content_preview`: First 100 characters of chunk content

**Answer Metadata:**
- `confidence_tier`: Tier 1-5
- `weakest_link_chunk_id`: Which chunk caused confidence downgrade
- `primary_source_count`: Number of FAQ/Rules chunks used
- `placeholder_count`: Number of placeholder chunks present
- `mapping_count`: Number of mapping chunks used
- `disclaimers_applied`: List of disclaimer types added
- `safety_rules_triggered`: List of safety rules that fired

**Performance Metadata:**
- `retrieval_duration_ms`: Time to retrieve chunks
- `generation_duration_ms`: Time to generate answer
- `total_duration_ms`: Total processing time

### Traceability Example

```json
{
  "query": {
    "original": "Does my Basic Family Plan cover dental?",
    "normalized": "basic family plan cover dental",
    "intent": "plan-specific",
    "timestamp": "2026-03-20T14:30:00Z"
  },
  "answer": {
    "text": "[Full answer text as shown above]",
    "confidence_tier": "Tier 3 (Moderate)",
    "disclaimers_applied": ["plan_confirmation", "placeholder_present"],
    "safety_rules_triggered": ["Plan confirmation required", "Placeholder present"]
  },
  "sources": [
    {
      "chunk_id": "FAQ-005",
      "source_file": "faq_chunks.jsonl",
      "source_chunk_id": "faq_dental_coverage_001",
      "chunk_type": "FAQ",
      "retrieval_score": 0.88,
      "confidence": "High",
      "status": "Approved",
      "is_placeholder": false,
      "safe_for_client_direct_use": true,
      "content_preview": "**Q: What types of dental coverage are available?**..."
    },
    {
      "chunk_id": "PLAN-003",
      "source_file": "plans_chunks.jsonl",
      "source_chunk_id": "plan_basic_family_placeholder",
      "chunk_type": "Plans",
      "retrieval_score": 0.068,
      "confidence": "Low",
      "status": "Pending Detail",
      "is_placeholder": true,
      "safe_for_client_direct_use": false,
      "content_preview": "**Basic Family Plan** [PLACEHOLDER]..."
    }
  ],
  "metadata": {
    "confidence_tier": "Tier 3",
    "weakest_link_chunk_id": "PLAN-003",
    "primary_source_count": 1,
    "placeholder_count": 1,
    "mapping_count": 0
  },
  "performance": {
    "retrieval_duration_ms": 145,
    "generation_duration_ms": 89,
    "total_duration_ms": 234
  }
}
```

---

## Answer Quality Guidelines

### Language and Tone

**Style:**
- Professional but approachable
- Clear and concise
- Patient-friendly (avoid jargon)
- Helpful and supportive

**Avoid:**
- ❌ Technical policy language (unless necessary)
- ❌ Legal jargon or fine print style
- ❌ Overly formal or bureaucratic tone
- ❌ Vague or evasive language

**Prefer:**
- ✅ Customer-friendly FAQ wording
- ✅ Concrete examples when possible
- ✅ Clear action steps
- ✅ Honest acknowledgment of limitations

---

### Length and Structure

**Target Length:**
- Tier 1 answers: 2-3 paragraphs (150-250 words)
- Tier 3 answers: 3-4 paragraphs (250-400 words) including disclaimers and verification steps
- Tier 5 answers: 1-2 paragraphs (100-150 words) safe fallback

**Structure:**
1. Lead with direct answer (1 paragraph)
2. Provide supporting detail (1-2 paragraphs)
3. Add verification steps if needed (bullets or numbered list)
4. Add disclaimers (clear formatting, **bold** if critical)
5. Provide contact info if needed

---

### Formatting

**Use:**
- ✅ Paragraphs for flowing text
- ✅ Bullet points for lists
- ✅ Numbered steps for processes
- ✅ **Bold** for critical disclaimers
- ✅ Clear section breaks

**Avoid:**
- ❌ Walls of text (break into paragraphs)
- ❌ Excessive bullet points
- ❌ ALL CAPS (except for critical warnings)
- ❌ Emojis or informal symbols

---

## Safety Behavior Summary

### What Prototype MUST Do

1. ✅ **Use FAQ/Rules as primary truth sources**
2. ✅ **Downweight placeholders heavily (score < 0.1)**
3. ✅ **Add mandatory disclaimers when placeholders present**
4. ✅ **Refuse to answer from placeholders alone (Tier 5 fallback)**
5. ✅ **Be honest about limitations**
6. ✅ **Maintain full source traceability**
7. ✅ **Apply weakest link rule for confidence**

### What Prototype MUST NOT Do

1. ❌ **NEVER state placeholder plan benefits as confirmed facts**
2. ❌ **NEVER confirm provider network status from placeholders**
3. ❌ **NEVER state placeholder costs/copays/deductibles as facts**
4. ❌ **NEVER display Mapping content directly to users**
5. ❌ **NEVER overstate confidence (prefer caution)**
6. ❌ **NEVER attempt answer from weak sources (Tier 5 → fallback)**

---

## Monitoring Response Quality

During internal testing, evaluate:

1. **Answer Truthfulness:**
   - Are answers based on reliable sources (FAQ/Rules)?
   - Are placeholders NEVER stated as facts?
   - Are limitations acknowledged honestly?

2. **Answer Completeness:**
   - Do answers address the query sufficiently?
   - Are verification steps provided when needed?
   - Are related topics mentioned when relevant?

3. **Answer Style:**
   - Is language customer-friendly?
   - Is structure clear and scannable?
   - Are disclaimers appropriately formatted?

4. **Disclaimer Appropriateness:**
   - Are disclaimers added when required?
   - Are disclaimers NOT added when unnecessary?
   - Are disclaimer wordings clear and actionable?

5. **Traceability Completeness:**
   - Can every answer be traced to sources?
   - Is weakest link correctly identified?
   - Are safety rules correctly logged?

---

## Document Control

**Filename:** PROTOTYPE_RESPONSE_BEHAVIOR.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_RETRIEVAL_FLOW.md - Step-by-step retrieval
- PROTOTYPE_QUERY_HANDLING.md - Query type strategies
- PROTOTYPE_EXCLUSIONS.md - What prototype must not do (next)
- PROTOTYPE_TEST_QUERIES.md - Test query set (next)
- HANDOFF_TO_ENGINEERING.md - Implementation handoff

---

**END OF RESPONSE BEHAVIOR SPECIFICATION**
