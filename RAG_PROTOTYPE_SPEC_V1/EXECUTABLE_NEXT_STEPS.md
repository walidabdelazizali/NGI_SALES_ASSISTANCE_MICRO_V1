# Executable Next Steps (Implementation Checklist)

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Actionable Guide)  

---

## Purpose

This optional guide provides **concrete, actionable steps** for implementing the Phase 1 RAG prototype. Each step includes:
- Clear deliverable
- Validation checkpoint
- Expected timeline
- Blocker criteria

Use this as a linear execution path. Complete each step fully before moving to the next.

---

## Overview: 4-6 Week Timeline

```
Week 1: Setup + Core Retrieval (Steps 1-4)
Week 2: Retrieval Flow + Safety (Steps 5-7)
Week 3: Testing + Validation (Steps 8-10)
End Week 3: Decision + Documentation (Steps 11-13)
```

**Go/No-Go Decision:** End of Week 3

---

## Step 1: Environment Setup (Day 1)

### Objective
Establish development environment and load source data.

### Actions
1. **Clone/access source data:**
   - Locate `C:\micro-insurance-kb-v1\KB_PACK_V1\`
   - Verify 87 chunks present:
     - FAQ layer: 20 chunks
     - Rules layer: 27 chunks
     - Mapping layer: 20 chunks
     - Plans layer: 15 chunks (placeholders)
     - Network layer: 5 chunks (placeholders)

2. **Choose technology stack:**
   - Embedding model (e.g., OpenAI text-embedding-3-small, Azure OpenAI, sentence-transformers)
   - Vector database (e.g., Chroma, FAISS, Pinecone, Azure AI Search)
   - Programming language (Python recommended)
   - Optional: Answer generation LLM (GPT-4, Claude, local model)

3. **Install dependencies:**
   ```bash
   pip install openai chromadb pandas python-dotenv
   # OR your chosen tech stack
   ```

4. **Set up project structure:**
   ```
   rag-prototype/
   ├── src/
   │   ├── ingest.py       # Data ingestion
   │   ├── retrieval.py    # Retrieval logic
   │   ├── confidence.py   # Tier calculation
   │   ├── safety.py       # Exclusions & disclaimers
   │   └── main.py         # Orchestration
   ├── data/
   │   └── kb_pack_v1/     # Copy of source chunks
   ├── tests/
   │   └── test_queries.py # Test query execution
   ├── config.py           # Configuration
   └── README.md
   ```

### Validation Checkpoint
- [ ] All 87 source chunks located and accessible
- [ ] Technology stack installed and tested
- [ ] Project structure created
- [ ] Basic "hello world" with embedding model working

### Blocker Criteria
❌ **STOP if:** Cannot access source chunks OR embedding model not working

### Timeline
**1 day** (Day 1)

---

## Step 2: Ingest FAQ Layer (Day 2)

### Objective
Ingest 20 FAQ chunks with full metadata and validate retrieval.

### Actions
1. **Load FAQ chunks:**
   - Read `FAQ-001.json` through `FAQ-020.json`
   - Parse all metadata fields:
     - `chunk_id`, `layer`, `content`, `metadata`
     - `is_placeholder`, `safe_for_client_direct_use`, `status`
     - `topic`, `subtopic`, `audience`, `confidence_level`

2. **Generate embeddings:**
   - Embed `content` text for each chunk
   - Store embeddings in vector database with full metadata

3. **Test retrieval:**
   - Query: "What is a deductible?"
   - Expected: Retrieve FAQ-001 (Deductible explanation) with high score (≥0.85)
   - Query: "Are pre-existing conditions covered?"
   - Expected: Retrieve FAQ-008 (Pre-existing conditions) with high score

### Validation Checkpoint
- [ ] All 20 FAQ chunks ingested
- [ ] FAQ-001 retrievable with high semantic match
- [ ] FAQ-008 retrievable for pre-existing query
- [ ] All metadata fields preserved

### Blocker Criteria
❌ **STOP if:** FAQ-001 semantic score <0.7 for "What is a deductible?" (retrieval quality too low)

### Timeline
**1 day** (Day 2)

---

## Step 3: Ingest Rules Layer (Day 2-3)

### Objective
Ingest 27 Rules chunks and validate policy question retrieval.

### Actions
1. **Load Rules chunks:**
   - Read `RULE-001.json` through `RULE-027.json`
   - Parse all metadata (same structure as FAQ)

2. **Generate embeddings:**
   - Embed `content` text for each chunk
   - Store with full metadata

3. **Test retrieval:**
   - Query: "What are the rules for pre-existing conditions?"
   - Expected: Retrieve RULE-007 (Pre-existing condition disclosure) with score ≥0.75
   - Query: "What services require prior authorization?"
   - Expected: Retrieve RULE-009 (Prior auth requirements)

### Validation Checkpoint
- [ ] All 27 Rules chunks ingested
- [ ] RULE-007 retrievable for pre-existing rules query
- [ ] Rules chunks have `type=rules` in metadata
- [ ] Cannot confuse FAQ and Rules layers (check metadata filtering)

### Blocker Criteria
❌ **STOP if:** Rules retrieval score <0.65 consistently (quality too low)

### Timeline
**0.5-1 day** (Day 2-3)

---

## Step 4: Ingest Mapping Layer (Day 3)

### Objective
Ingest 20 Mapping chunks for cross-reference support.

### Actions
1. **Load Mapping chunks:**
   - Read `MAP-001.json` through `MAP-020.json`
   - Parse metadata including `cross_references`

2. **Generate embeddings:**
   - Embed `content` text
   - Store with full metadata

3. **Test retrieval:**
   - Query: "What's the relationship between deductible and out-of-pocket max?"
   - Expected: Retrieve MAP-005 (Deductible-OOP relationship) or similar

### Validation Checkpoint
- [ ] All 20 Mapping chunks ingested
- [ ] Mapping chunks retrievable
- [ ] `cross_references` metadata preserved
- [ ] Can retrieve cross-links for complex queries

### Blocker Criteria
❌ **STOP if:** Cannot retrieve any Mapping chunks (ingestion failed)

### Timeline
**0.5 day** (Day 3)

---

## Step 5: Ingest Placeholder Layers with Downweighting (Day 3-4)

### Objective
Ingest 20 placeholder chunks (15 Plans + 5 Network) with MANDATORY downweighting penalty applied.

### Actions
1. **Load Plans layer:**
   - Read `PLAN-001.json` through `PLAN-015.json`
   - Verify `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`

2. **Load Network layer:**
   - Read `PROV-001.json` through `PROV-005.json`
   - Verify `is_placeholder=TRUE`

3. **Implement downweighting:**
   ```python
   # After retrieval, before ranking:
   for chunk in retrieved_chunks:
       if chunk.metadata["is_placeholder"] == True:
           chunk.base_weight = 0.2  # Layer weight
           chunk.penalty = 0.08      # Placeholder penalty
           chunk.final_score = chunk.semantic_score * chunk.base_weight * chunk.penalty
           # Example: 0.85 semantic * 0.2 weight * 0.08 penalty = 0.0136 final score (<0.1)
   ```

4. **Test downweighting:**
   - Query: "Does Basic Family Plan cover dental?"
   - Expected retrieval:
     - FAQ-005 (Dental general): score 0.88
     - PLAN-003 (Basic Family Plan): semantic 0.75 → final **0.012** (<0.1), **ranked very low**
   - Verify: PLAN-003 appears in results BUT with score <0.1, NOT top result

### Validation Checkpoint
- [ ] All 20 placeholder chunks ingested
- [ ] Downweighting formula implemented correctly
- [ ] PLAN-003 final score <0.1 for dental query
- [ ] Placeholders appear in retrieval BUT ranked very low
- [ ] FAQ-005 still top result despite PLAN-003 present

### Blocker Criteria
❌ **CRITICAL STOP if:** Placeholder score ≥0.1 after downweighting (safety failure)

### Timeline
**1 day** (Day 3-4)

---

## Step 6: Implement is_placeholder Filtering (Day 4)

### Objective
Add safety filter to exclude placeholders from direct answer generation.

### Actions
1. **Implement filtering logic:**
   ```python
   def filter_sources_for_answer(retrieved_chunks):
       """Separate sources by safety for direct answer use."""
       safe_sources = []
       context_only_sources = []
       
       for chunk in retrieved_chunks:
           if chunk.metadata.get("is_placeholder") == True:
               # Placeholders: context only, NEVER state details
               context_only_sources.append(chunk)
           elif chunk.metadata.get("safe_for_client_direct_use") == True:
               # FAQ/Rules/Mapping: safe for direct answers
               safe_sources.append(chunk)
       
       return safe_sources, context_only_sources
   ```

2. **Test filtering:**
   - Query: "Does Basic Family Plan cover dental?"
   - Retrieved: FAQ-005 (safe), PLAN-003 (placeholder)
   - Expected:
     - `safe_sources`: [FAQ-005]
     - `context_only_sources`: [PLAN-003]
     - Answer generated ONLY from FAQ-005
     - PLAN-003 name recognized from context, details NOT stated

### Validation Checkpoint
- [ ] Filtering function implemented
- [ ] Placeholders separated into `context_only_sources`
- [ ] Answer generation uses ONLY `safe_sources`
- [ ] Can still recognize plan/provider names from context

### Blocker Criteria
❌ **CRITICAL STOP if:** Placeholder content appears in generated answer as factual statement

### Timeline
**0.5 day** (Day 4)

---

## Step 7: Implement 8-Step Retrieval Flow (Day 4-5)

### Objective
Build full retrieval flow from query normalization to answer generation.

### Actions
1. **Implement flow steps:**
   ```python
   def retrieve_and_answer(query):
       # Step 1: Normalize query
       normalized = normalize_query(query)
       
       # Step 2-4: Retrieve from each layer
       faq_results = retrieve_faq(normalized, top_k=5)
       rules_results = retrieve_rules(normalized, top_k=4)
       mapping_results = retrieve_mapping(normalized, top_k=3)
       placeholder_results = retrieve_placeholders(normalized, top_k=2)
       
       # Step 5: Apply placeholder downweighting
       placeholder_results = apply_placeholder_penalty(placeholder_results)
       
       # Step 6: Assemble sources (safe vs context-only)
       safe_sources, context_sources = filter_sources_for_answer(
           faq_results + rules_results + mapping_results + placeholder_results
       )
       
       # Step 7: Calculate confidence tier (implement in Step 8)
       tier = calculate_confidence_tier(safe_sources, context_sources)
       
       # Step 8: Generate answer by tier (implement in Step 9)
       answer = generate_answer_by_tier(query, safe_sources, context_sources, tier)
       
       return answer
   ```

2. **Test flow end-to-end:**
   - Query: "What is a deductible?"
   - Verify all 8 steps execute
   - Check: FAQ retrieved → no placeholders → Tier 1 expected

### Validation Checkpoint
- [ ] All 8 steps implemented
- [ ] Flow executes end-to-end without errors
- [ ] Can retrieve from multiple layers
- [ ] Downweighting applied automatically

### Blocker Criteria
❌ **STOP if:** Retrieval flow crashes or produces no results for basic queries

### Timeline
**1 day** (Day 4-5)

---

## Step 8: Implement Confidence Tier Logic (Day 5-6)

### Objective
Calculate confidence tiers (Tier 1-5) using weakest link rule.

### Actions
1. **Implement tier calculation:**
   ```python
   def calculate_confidence_tier(safe_sources, context_sources):
       """Calculate confidence tier using weakest link rule."""
       
       # Check for placeholders (automatic Tier 3 downgrade)
       if len(context_sources) > 0:  # Any is_placeholder=TRUE
           return "Tier 3"  # Moderate, MANDATORY disclaimers
       
       # Check semantic scores
       if len(safe_sources) == 0:
           return "Tier 5"  # Unsafe, fallback
       
       max_score = max([s.semantic_score for s in safe_sources])
       
       # Check source mix
       has_faq = any(s.layer == "faq" for s in safe_sources)
       has_rules = any(s.layer == "rules" for s in safe_sources)
       has_mapping = any(s.layer == "mapping" for s in safe_sources)
       
       # Tier 1: FAQ + Rules, high semantic, no placeholders
       if has_faq and has_rules and max_score >= 0.7:
           return "Tier 1"
       
       # Tier 2: FAQ + Rules + Mapping, no placeholders
       if (has_faq or has_rules) and has_mapping and max_score >= 0.6:
           return "Tier 2"
       
       # Tier 4: Rules-only or low confidence
       if has_rules and max_score < 0.7:
           return "Tier 4"
       
       # Default: Tier 3 (moderate caution)
       return "Tier 3"
   ```

2. **Test tier calculation:**
   - "What is a deductible?" → FAQ-001 + RULE-001, no placeholder → **Tier 1**
   - "Does Basic Family Plan cover dental?" → FAQ-005 + PLAN-003 → **Tier 3**
   - "What's my claim status?" → Low match → **Tier 5**

### Validation Checkpoint
- [ ] Tier logic implemented
- [ ] Placeholder presence triggers Tier 3 downgrade
- [ ] Weakest link rule applied
- [ ] Test queries produce expected tiers

### Blocker Criteria
❌ **STOP if:** Placeholder query returns Tier 1 (should be Tier 3)

### Timeline
**1 day** (Day 5-6)

---

## Step 9: Implement Mandatory Disclaimer Logic (Day 6-7)

### Objective
Detect 6 disclaimer situations and attach appropriate disclaimers.

### Actions
1. **Implement disclaimer detection:**
   ```python
   def determine_disclaimers(query, safe_sources, context_sources, tier):
       """Determine which disclaimers are mandatory."""
       disclaimers = []
       
       # 1. Plan confirmation disclaimer
       if any_plan_name_in_query(query) or len(context_sources) > 0:
           disclaimers.append({
               "type": "plan_confirmation",
               "text": "Coverage details vary by plan. Check your policy documents or contact customer service."
           })
       
       # 2. Network verification disclaimer
       if any_network_keyword_in_query(query) or any_network_placeholder(context_sources):
           disclaimers.append({
               "type": "network_verification",
               "text": "Provider network status may vary. Always verify with customer service before scheduling your appointment."
           })
       
       # 3. Placeholder present disclaimer
       if len(context_sources) > 0:
           disclaimers.append({
               "type": "placeholder_present",
               "text": "For plan-specific details, check your policy documents or contact customer service at [number]."
           })
       
       # 4-6: Implement other disclaimer situations...
       
       return disclaimers
   ```

2. **Test disclaimer attachment:**
   - "Does Basic Family Plan cover dental?" → Plan name detected → **MANDATORY plan disclaimer**
   - "Is Dr. Ahmed in-network?" → Network keyword → **MANDATORY network disclaimer**
   - "What is a deductible?" → Clean query → **NO disclaimers**

### Validation Checkpoint
- [ ] Disclaimer logic implemented for all 6 situations
- [ ] Plan-specific query triggers disclaimer
- [ ] Network query triggers disclaimer
- [ ] Clean conceptual query has NO unnecessary disclaimers
- [ ] Disclaimers attached to answer metadata

### Blocker Criteria
❌ **CRITICAL STOP if:** Plan/network query missing mandatory disclaimer (safety failure)

### Timeline
**1 day** (Day 6-7)

---

## Step 10: Implement Exclusion Violation Detection (Day 7-8)

### Objective
Detect and BLOCK 9 critical exclusions before answer is returned.

### Actions
1. **Implement violation detection:**
   ```python
   def detect_exclusion_violations(answer_text, context_sources):
       """Detect CRITICAL exclusion violations. Return violations list."""
       violations = []
       
       # Exclusion 1: Placeholder benefit details stated as fact
       if contains_placeholder_benefit_statement(answer_text, context_sources):
           violations.append({
               "exclusion": 1,
               "severity": "CRITICAL",
               "description": "Answer states placeholder plan benefit as confirmed fact"
           })
       
       # Exclusion 2: Network status confirmed from placeholder
       if contains_network_status_confirmation(answer_text, context_sources):
           violations.append({
               "exclusion": 2,
               "severity": "CRITICAL",
               "description": "Answer confirms network status from placeholder data"
           })
       
       # Exclusion 3: Specific cost from placeholder
       if contains_cost_statement_from_placeholder(answer_text, context_sources):
           violations.append({
               "exclusion": 3,
               "severity": "CRITICAL",
               "description": "Answer provides specific cost from placeholder"
           })
       
       # Exclusions 4-9: Implement remaining...
       
       return violations
   
   def block_if_critical(violations):
       """Block answer if CRITICAL violations detected."""
       critical = [v for v in violations if v["severity"] == "CRITICAL"]
       if len(critical) > 0:
           raise SafetyViolationError(f"CRITICAL violations: {critical}")
   ```

2. **Test violation detection:**
   - Simulate answer: "Yes, Basic Family Plan covers dental with 80% coinsurance" + PLAN-003 placeholder
   - Expected: **BLOCKED** (Exclusion 1 CRITICAL violation)
   - Simulate answer: "Yes, Dr. Ahmed is in-network" + PROV-002 placeholder
   - Expected: **BLOCKED** (Exclusion 2 CRITICAL violation)

### Validation Checkpoint
- [ ] Violation detection implemented for all 9 exclusions
- [ ] CRITICAL violations (1-3) block answer before return
- [ ] HIGH/MEDIUM violations logged but may not block
- [ ] Test violations successfully blocked

### Blocker Criteria
❌ **CRITICAL STOP if:** Placeholder benefit statement NOT detected and blocked

### Timeline
**1 day** (Day 7-8)

---

## Step 11: Implement Answer Generation by Tier (Day 8-9)

### Objective
Generate appropriate answers based on confidence tier.

### Actions
1. **Implement tier-based generation:**
   ```python
   def generate_answer_by_tier(query, safe_sources, context_sources, tier, disclaimers):
       """Generate answer appropriate for confidence tier."""
       
       if tier == "Tier 1":
           # Confident, direct answer from FAQ/Rules
           answer = generate_confident_answer(query, safe_sources)
           # No disclaimers typically
       
       elif tier == "Tier 2":
           # Strong answer with cross-references
           answer = generate_strong_answer(query, safe_sources)
           # Minimal disclaimers
       
       elif tier == "Tier 3":
           # Cautious, general guidance + disclaimers
           answer = generate_cautious_answer(query, safe_sources, context_sources)
           answer += "\n\n" + format_disclaimers(disclaimers)  # MANDATORY
       
       elif tier == "Tier 4":
           # Weak, policy guidance only
           answer = generate_weak_answer(query, safe_sources)
           answer += "\n\nFor personalized assistance, contact customer service."
       
       elif tier == "Tier 5":
           # Unsafe, fallback
           answer = generate_fallback_answer(query)
       
       return answer
   ```

2. **Test answer generation:**
   - Tier 1 query → Confident, no disclaimers
   - Tier 3 query → Cautious, MANDATORY disclaimers present
   - Tier 5 query → Safe fallback

### Validation Checkpoint
- [ ] Answer generation for all 5 tiers implemented
- [ ] Tier 1 answers confident and direct
- [ ] Tier 3 answers include mandatory disclaimers
- [ ] Tier 5 answers provide safe fallback
- [ ] No placeholder details in any tier

### Blocker Criteria
❌ **STOP if:** Tier 3 answer missing mandatory disclaimers

### Timeline
**1 day** (Day 8-9)

---

## Step 12: Implement Full Traceability Metadata (Day 9-10)

### Objective
Attach comprehensive metadata to every answer for full traceability.

### Actions
1. **Implement metadata structure:**
   ```python
   def build_traceability_metadata(query, sources, tier, disclaimers, violations, performance):
       """Build complete traceability metadata."""
       return {
           "query_metadata": {
               "original_query": query,
               "normalized_query": normalize_query(query),
               "query_type": classify_query_type(query),
               "timestamp": datetime.now().isoformat()
           },
           "source_metadata": {
               "retrieved_chunks": [
                   {
                       "chunk_id": s.chunk_id,
                       "layer": s.layer,
                       "semantic_score": s.semantic_score,
                       "final_score": s.final_score,
                       "is_placeholder": s.is_placeholder,
                       "safe_for_client_direct_use": s.safe_for_client_direct_use
                   }
                   for s in sources
               ],
               "safe_sources_count": len([s for s in sources if not s.is_placeholder]),
               "context_only_count": len([s for s in sources if s.is_placeholder])
           },
           "answer_metadata": {
               "confidence_tier": tier,
               "disclaimers_applied": [d["type"] for d in disclaimers],
               "exclusion_violations": violations,
               "weakest_source": identify_weakest_source(sources)
           },
           "performance_metadata": {
               "retrieval_time_ms": performance.retrieval_time,
               "total_time_ms": performance.total_time
           }
       }
   ```

2. **Attach to every answer:**
   - Include full metadata in response
   - Log to file or database for audit trail

### Validation Checkpoint
- [ ] Metadata structure implemented
- [ ] All 4 metadata categories present (query/source/answer/performance)
- [ ] Metadata attached to every answer
- [ ] Can audit complete retrieval path from metadata

### Blocker Criteria
❌ **STOP if:** Cannot trace answer back to source chunks (traceability failure)

### Timeline
**1 day** (Day 9-10)

---

## Step 13: Run 30 Core Test Queries (Day 10-14)

### Objective
Execute all 30 test queries from PROTOTYPE_TEST_QUERIES.md and validate results.

### Actions
1. **Load test queries:**
   - Open `PROTOTYPE_TEST_QUERIES.md`
   - Extract all 30 queries across 8 categories

2. **Execute each query:**
   - Run through full retrieval flow
   - Record results using template from INTERNAL_TESTING_PLAN.md:
     ```
     Query ID: TC-01
     Query: "What is a deductible?"
     Expected Tier: Tier 1
     Actual Tier: [RECORD]
     Expected Disclaimers: None
     Actual Disclaimers: [RECORD]
     Expected Primary Sources: FAQ-001
     Actual Primary Sources: [RECORD]
     Safety Violations: [RECORD]
     Pass/Fail: [RECORD]
     Notes: [RECORD]
     ```

3. **Validate CRITICAL requirements:**
   - **CRITICAL 1:** Zero placeholder leakage (check all plan/network queries)
   - **CRITICAL 2:** 100% mandatory disclaimer presence (check Tier 3 queries)
   - **CRITICAL 3:** Placeholder downweighting <0.1 (check all placeholder scores)
   - **CRITICAL 4:** 100% source metadata (check all answers)
   - **CRITICAL 5:** 100% answer metadata (check all answers)
   - **CRITICAL 6:** 0% inappropriate operations (check account/claims queries)

### Validation Checkpoint
- [ ] All 30 test queries executed
- [ ] Results recorded in template format
- [ ] ALL 6 CRITICAL requirements pass
- [ ] ≥4 of 6 HIGH requirements pass (for Minimum Viable Success)
- [ ] No CRITICAL safety violations detected

### Blocker Criteria
❌ **STOP TESTING if:** Any CRITICAL safety violation detected (placeholder leakage, missing mandatory disclaimer)  
❌ **NO-GO if:** <6 of 6 CRITICAL requirements pass OR <4 of 6 HIGH requirements pass

### Timeline
**3-4 days** (Day 10-14, includes analysis)

---

## Step 14: Safety Violation Testing (Day 14-15)

### Objective
Attempt to trigger safety violations and verify they are blocked.

### Actions
1. **Attempt violation triggers:**
   - Try to force placeholder benefit statement
   - Try to confirm network status from placeholder
   - Try to state cost from placeholder
   - Try to perform account operation
   - Try to make claims adjudication

2. **Verify all violations blocked:**
   - Expected: **0 successful violations** (all blocked)
   - If ANY violation succeeds: **CRITICAL FAILURE, STOP TESTING**

### Validation Checkpoint
- [ ] Attempted all 9 exclusion violations
- [ ] **100% blocked** (0 successful violations)
- [ ] CRITICAL violations trigger immediate blocking
- [ ] HIGH/MEDIUM violations logged

### Blocker Criteria
❌ **CRITICAL FAILURE if:** Any CRITICAL violation (1-3) succeeds (automatically NO-GO)

### Timeline
**1 day** (Day 14-15)

---

## Step 15: KB Quality Assessment (Day 15-16)

### Objective
Identify gaps, weaknesses, and improvement opportunities in KB_PACK_V1.

### Actions
1. **Review test results:**
   - Which queries had low retrieval quality?
   - Which topics had no strong FAQ/Rules coverage?
   - Which queries required Tier 4-5 (weak/unsafe)?

2. **Document KB gaps:**
   Use template from INTERNAL_TESTING_PLAN.md:
   ```
   Gap ID: GAP-01
   Topic/Query: [RECORD]
   Current Coverage: [Weak/None/Placeholder-only]
   Impact: [High/Medium/Low]
   Recommended Action: [Create new FAQ, enhance Rules, etc.]
   Priority for Phase 2: [P0/P1/P2]
   ```

3. **Compile gap report:**
   - Target: ≥5 gaps identified (demonstrates prototype value)

### Validation Checkpoint
- [ ] KB gaps identified and documented
- [ ] ≥5 gaps documented
- [ ] Each gap has recommended action
- [ ] Report demonstrates prototype value (identifying weaknesses)

### Blocker Criteria
❌ **NO-GO if:** Cannot identify any gaps (suggests testing wasn't thorough)

### Timeline
**1-2 days** (Day 15-16)

---

## Step 16: Compile Test Results Summary (Day 17-18)

### Objective
Create comprehensive test results report for GO/NO-GO decision.

### Actions
1. **Calculate metrics:**
   - CRITICAL requirements: X of 6 passed
   - HIGH requirements: X of 6 passed
   - FAQ retrieval relevance: X%
   - Rules retrieval relevance: X%
   - Answer relevance: X%
   - Safety compliance: X%

   from PROTOTYPE_SUCCESS_CRITERIA.md:
   ```
   CRITICAL (ALL must pass):
   ✅/❌ Zero placeholder leakage: 0%
   ✅/❌ Mandatory disclaimers: 100%
   ✅/❌ Placeholder downweighting: <0.1
   ✅/❌ Source metadata: 100%
   ✅/❌ Answer metadata: 100%
   ✅/❌ No inappropriate operations: 0%
   
   HIGH (≥4 must pass):
   ✅/❌ FAQ retrieval: ≥85%
   ✅/❌ Rules retrieval: ≥80%
   ✅/❌ Answer relevance: ≥80%
   ✅/❌ Customer-friendly language: ≥90%
   ✅/❌ Answer structure: ≥85%
   ✅/❌ Engineering confidence: ✅
   ```

2. **Make GO/NO-GO recommendation:**
   - **GO if:** ALL 6 CRITICAL + ≥4 of 6 HIGH requirements pass
   - **NO-GO if:** Any CRITICAL fails OR <4 HIGH pass

3. **Write report:**
   - Executive summary (1 page)
   - Detailed test results (all 30 queries)
   - Safety compliance certificate
   - KB quality assessment
   - Phase 2 recommendations

### Validation Checkpoint
- [ ] All metrics calculated
- [ ] GO/NO-GO decision made based on criteria
- [ ] Full report compiled
- [ ] Ready for stakeholder review

### Blocker Criteria
❌ **NO-GO if:** Not meeting Minimum Viable Success criteria

### Timeline
**1-2 days** (Day 17-18)

---

## Step 17: Stakeholder Review & Decision (Day 19-20)

### Objective
Present results to stakeholders and obtain sign-off for Phase 2.

### Actions
1. **Schedule reviews:**
   - Knowledge Engineering team
   - Product team
   - Compliance team
   - Engineering leadership

2. **Present findings:**
   - Test results summary
   - Safety compliance status
   - KB quality gaps identified
   - Phase 2 recommendations

3. **Obtain sign-off:**
   - Collect approval or feedback from all 4 teams
   - Document any concerns or conditions

### Validation Checkpoint
- [ ] All stakeholder reviews completed
- [ ] Sign-off obtained from 4 teams
- [ ] Concerns documented and addressed
- [ ] GO/NO-GO decision finalized

### Blocker Criteria
❌ **NO-GO if:** Compliance team or Engineering leadership reject

### Timeline
**1-2 days** (Day 19-20)

---

## Step 18: Document Lessons Learned (Day 20-21)

### Objective
Capture insights and prepare for Phase 2.

### Actions
1. **Document lessons:**
   - What worked well?
   - What challenges encountered?
   - What would you do differently?
   - What surprised you?

2. **Create Phase 2 plan:**
   - Which KB gaps to address first?
   - What retrieval improvements needed?
   - What additional safety rules needed?
   - Timeline for Phase 2 implementation

3. **Archive prototype:**
   - Save code repository
   - Save test results
   - Save all documentation

### Validation Checkpoint
- [ ] Lessons learned documented
- [ ] Phase 2 plan created
- [ ] Prototype archived
- [ ] Handoff complete

### Timeline
**1 day** (Day 20-21)

---

## Summary: Linear Execution Path

```
✅ Week 1: Setup + Core Retrieval
   Day 1: Environment setup
   Day 2: Ingest FAQ
   Day 2-3: Ingest Rules
   Day 3: Ingest Mapping
   Day 3-4: Ingest placeholders with downweighting
   Day 4: Implement is_placeholder filtering

✅ Week 2: Retrieval Flow + Safety
   Day 4-5: Implement 8-step retrieval flow
   Day 5-6: Implement confidence tier logic
   Day 6-7: Implement mandatory disclaimer logic
   Day 7-8: Implement exclusion violation detection
   Day 8-9: Implement answer generation by tier
   Day 9-10: Implement traceability metadata

✅ Week 3: Testing + Validation
   Day 10-14: Run 30 core test queries
   Day 14-15: Safety violation testing
   Day 15-16: KB quality assessment
   Day 17-18: Compile test results summary
   Day 19-20: Stakeholder review & decision
   Day 20-21: Document lessons learned

🔍 End Week 3: GO/NO-GO Decision
   GO: Proceed to Phase 2 (Placeholder Enrichment)
   NO-GO: Address CRITICAL failures, re-test
```

---

## Red Flags: When to STOP

**CRITICAL STOP conditions (stop testing immediately):**
1. ❌ Placeholder benefit details stated as fact (Exclusion 1 violation)
2. ❌ Network status confirmed from placeholder (Exclusion 2 violation)
3. ❌ Specific cost from placeholder stated (Exclusion 3 violation)
4. ❌ Missing mandatory plan confirmation disclaimer
5. ❌ Missing mandatory network verification disclaimer
6. ❌ Placeholder final score ≥0.1 after downweighting
7. ❌ Cannot trace answer back to source chunks (traceability failure)
8. ❌ >3 CRITICAL violations in first 10 test queries

**NO-GO conditions (do not proceed to Phase 2):**
- ❌ <6 of 6 CRITICAL requirements pass
- ❌ <4 of 6 HIGH requirements pass
- ❌ Any CRITICAL safety violation succeeded (not blocked)
- ❌ Compliance team rejects prototype

---

## Success Indicators: When to GO

**GO decision criteria:**
- ✅ ALL 6 CRITICAL requirements pass (100%)
- ✅ ≥4 of 6 HIGH requirements pass
- ✅ 0 successful safety violations (all blocked)
- ✅ ≥5 KB gaps identified
- ✅ All 4 stakeholder teams sign off
- ✅ Engineering confidence in implementation

**Strong GO indicators:**
- ✅ FAQ retrieval ≥85% relevance
- ✅ Rules retrieval ≥80% relevance
- ✅ Answer relevance ≥80%
- ✅ 100% mandatory disclaimer presence
- ✅ 0% placeholder leakage
- ✅ Full traceability metadata on all answers

---

## Document Control

**Filename:** EXECUTABLE_NEXT_STEPS.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification (Optional Actionable Guide)  

**Related Documents:**
- HANDOFF_TO_ENGINEERING.md - Comprehensive implementation guide
- INTERNAL_TESTING_PLAN.md - Detailed testing methodology
- PROTOTYPE_TEST_QUERIES.md - 30 test queries  
content
- PROTOTYPE_SUCCESS_CRITERIA.md - GO/NO-GO criteria
- PROTOTYPE_DECISION_TABLE.md - Quick reference

**Purpose:** This document provides a linear, step-by-step execution path for implementing the Phase 1 RAG prototype. Follow these 18 steps sequentially to complete implementation and testing in 3-4 weeks.

---

**END OF EXECUTABLE NEXT STEPS**
