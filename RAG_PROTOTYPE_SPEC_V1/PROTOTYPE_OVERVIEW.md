# RAG Prototype Specification V1 - Overview

**Version:** 1.0  
**Date:** March 19, 2026  
**Status:** Internal Testing Only  
**Audience:** Internal engineering team, QA, product team  

---

## What This Prototype Is

The **RAG Prototype V1** is a **concrete specification** for building an **internal-only retrieval system** that enables safe, controlled testing of the Micro Insurance Knowledge Base V1 in a retrieval-augmented generation (RAG) context.

**Purpose:**
- Enable internal teams to test knowledge retrieval behavior before customer-facing deployment
- Validate that FAQ and Rules content can safely answer common insurance questions
- Demonstrate the trust hierarchy in action (FAQ/Rules > Mapping > Placeholders)
- Identify gaps in knowledge base coverage
- Collect evidence for Phase B deployment readiness (see RAG_EXECUTION_SPEC_V1)

**Scope:**
- Internal testing environment only
- 67 strong knowledge chunks (FAQ + Rules + Mapping) as primary sources
- Conservative answer behavior (explicit caution when certainty is limited)
- Traceability to source chunks for validation
- No customer-facing deployment in Phase 1

**Key Design Principle:**
> **Prioritize truthfulness over completeness.** Better to say "check your policy documents" than to overstate placeholder content as confirmed insurance truth.

---

## What This Prototype Is NOT

This prototype specification is **not**:

❌ **NOT a production system** - Internal testing only, no customer-facing deployment yet  
❌ **NOT a complete insurance platform** - Retrieval testing only, no claims processing, underwriting, or operations  
❌ **NOT a bot or UI** - Specification only, implementation teams choose interface (CLI, web, API, etc.)  
❌ **NOT infrastructure code** - No deployment scripts, no cloud configuration, no runtime code  
❌ **NOT a final product** - First phase of gradual rollout (Phase B → Phase C → Production)  
❌ **NOT using real plan data** - Plans layer is placeholder-only in Phase 1  
❌ **NOT using live provider network** - Network layer is placeholder-only in Phase 1  

**This is a specification document**, not executable code. Implementation teams will use this spec to build the actual prototype.

---

## Why This Prototype Exists Now

### The Challenge

The approved Knowledge Base V1 contains:
- **67 strong chunks** (FAQ + Rules + Mapping): High confidence, ready for use
- **20 placeholder chunks** (Plans + Network): Low confidence, structural scaffolding only

**Problem:** We need to validate retrieval behavior before customer-facing deployment, but we can't wait 6 months for real plan/network data.

**Solution:** Build an internal prototype that:
1. Uses strong knowledge (FAQ/Rules/Mapping) for primary answers
2. Treats placeholders as weak context only (never primary facts)
3. Tests retrieval quality in a controlled environment
4. Identifies knowledge gaps for prioritized FAQ/Rules expansion

---

### The Opportunity

This prototype enables:

**For Product:** Validate that knowledge base can answer common questions with acceptable quality  
**For Engineering:** Test retrieval algorithms and trust hierarchy enforcement before full implementation  
**For QA:** Identify failure modes, unsafe answers, and knowledge gaps  
**For Compliance:** Review answer behavior with placeholder guardrails before pilot  
**For Content:** Discover which FAQ/Rules need improvement or expansion  

**Outcome:** Evidence-based decision for Phase C deployment readiness (limited pilot with placeholder guardrails)

---

## How This Prototype Uses Existing Materials

This prototype specification builds directly on approved materials:

### 1. Knowledge Base Package (KB_PACK_V1)

**Location:** `C:\micro-insurance-kb-v1\KB_PACK_V1`

**Contents:**
- 20 FAQ chunks (customer-facing explanations)
- 27 Rules chunks (policy reasoning and benefit rules)
- 20 Mapping chunks (cross-reference relationships)
- 10 Plans chunks (placeholder structural scaffolding)
- 10 Network chunks (placeholder structural scaffolding)

**How Prototype Uses This:**
- **Primary sources:** FAQ (20) + Rules (27) + Mapping (20) = 67 strong chunks
- **Secondary context:** Plans (10) + Network (10) = 20 placeholders (not primary answer sources)

---

### 2. RAG Policy (RAG_POLICY_V1)

**Location:** `C:\micro-insurance-kb-v1\RAG_POLICY_V1`

**Contents:**
- Trust hierarchy principles (FAQ/Rules stronger than placeholders)
- Metadata strategy (40+ fields including safety flags)
- Placeholder handling policy (allowed vs forbidden uses)
- Answer safety principles (weakest link rule)

**How Prototype Uses This:**
- Enforces trust hierarchy: FAQ/Rules always dominate placeholders
- Applies safety metadata: `is_placeholder`, `safe_for_client_direct_use`, `requires_plan_confirmation`
- Follows placeholder policy: Placeholders for context only, never primary answer facts
- Implements conservative answer behavior: Explicit caution when certainty is limited

---

### 3. RAG Execution Specification (RAG_EXECUTION_SPEC_V1)

**Location:** `C:\micro-insurance-kb-v1\RAG_EXECUTION_SPEC_V1`

**Contents:**
- 2-phase ingestion sequencing (Phase 1: FAQ+Rules+Mapping, Phase 2: Placeholders)
- Metadata derivation rules (9 categories, 40+ fields)
- Filtering strategies (4 use cases: customer STRICT, internal MODERATE, self-service VERY STRICT, developer NO FILTERING)
- Weight formula ensuring FAQ/Rules dominate by 12.5x over placeholders
- 5-phase rollout plan (A: Metadata intake, B: Internal testing, C: Pilot, D: Real data, E: Production)

**How Prototype Uses This:**
- **Phase B target:** Internal testing with FAQ+Rules+Mapping only (can optionally add placeholders with strict downranking)
- **Trust hierarchy enforcement:** Weight formula, filtering, status multipliers
- **Conservative behavior:** Answer safety scenarios (7 scenarios from strongest to unsafe)
- **Validation criteria:** Retrieval quality ≥85%, placeholder leak rate 0%, disclaimer presence 100%

---

## Why This Prototype Is Internal-Only

### Safety First

**Internal-only status protects against:**

1. **Incomplete knowledge:** Plans and Network layers are placeholders, not confirmed product/provider data
2. **Unvalidated retrieval:** Retrieval quality not yet proven at scale
3. **Insufficient testing:** Need internal validation before external exposure
4. **Regulatory risk:** Compliance approval required before customer-facing deployment

---

### Controlled Learning Environment

**Internal-only enables:**

1. **Safe experimentation:** Test retrieval behavior without customer impact
2. **Rapid iteration:** Adjust weights, filters, and answer behavior based on findings
3. **Knowledge gap discovery:** Identify missing FAQ/Rules content without customer frustration
4. **Team training:** Build internal expertise before scaling

---

### Deployment Progression

**Gradual rollout path:**

```
Phase 1 (NOW):     Internal Prototype (this spec)
                   ↓
Phase 2 (2-3 weeks): Internal Testing (FAQ+Rules+Mapping only)
                   ↓
Phase 3 (4-6 weeks): Limited Pilot (Add placeholders with guardrails, 10-20 customers)
                   ↓
Phase 4 (3-6 months): Production (Replace placeholders with real data)
```

**This prototype specification defines Phase 1 only.** Progression to Phase 2+ requires:
- Gate A approval (data quality, ingestion quality, retrieval quality ≥85%, infrastructure ready)
- Internal testing feedback positive
- No critical bugs
- Compliance readiness for next phase

---

## Prototype Design Philosophy

### 1. Conservative by Default

**Principle:** When uncertain, defer to authoritative sources rather than generating potentially incorrect answers.

**Implementation:**
- Use FAQ for customer-safe wording (avoid internal jargon)
- Use Rules for policy logic and interpretation
- Say "check your policy documents" when plan-specific truth is needed
- Say "verify provider network status" when network confirmation is needed
- Be honest when prototype lacks enough evidence

---

### 2. Traceability

**Principle:** Every answer must be traceable to source chunks and original source files.

**Implementation:**
- Preserve `chunk_id` for every retrieved chunk
- Preserve `source_file` and `source_id` for audit trail
- Enable internal reviewers to verify answer → chunk → source file path
- Support "show me your sources" queries for debugging

---

### 3. Trust Hierarchy Enforcement

**Principle:** FAQ and Rules are stronger sources than placeholders.

**Implementation:**
- FAQ/Rules always dominate retrieval results (12.5x weight advantage)
- Placeholders downranked heavily (score 0.068 vs FAQ 0.85 for identical semantic match)
- Placeholders used for context awareness only, never primary answer facts
- Internal users see placeholder warnings: "⚠️ PLACEHOLDER - Not confirmed product data"

---

### 4. Explicit Limitations

**Principle:** Be clear about what the prototype can and cannot do.

**Implementation:**
- Display limitations notice during internal testing
- Flag plan-dependent questions requiring policy confirmation
- Flag network-dependent questions requiring live verification
- Refuse questions outside knowledge base scope (e.g., claims adjudication, underwriting)

---

## Success Criteria for This Prototype

This prototype is considered successful if:

✅ **Retrieval Quality:** FAQ/Rules chunks retrieved for ≥85% of common insurance questions  
✅ **No False Certainty:** Placeholder content never overstated as confirmed product/provider facts  
✅ **Conservative Answers:** Appropriate caution/disclaimers for plan/network-dependent questions  
✅ **Traceability:** All answers traceable to source chunks and files  
✅ **Knowledge Gap Discovery:** Identifies 10+ specific FAQ/Rules additions needed  
✅ **Internal Validation:** Engineering, QA, and product teams confirm answer quality acceptable  
✅ **Gate A Readiness:** Meets all criteria for internal testing deployment (see DEPLOYMENT_READINESS_GATES.md)  

**Failure modes to avoid:**
- ❌ Placeholder plan benefits stated as confirmed product facts
- ❌ Placeholder provider network status confirmed without verification
- ❌ Confident answers when prototype lacks evidence
- ❌ Missing disclaimers for plan/network-dependent questions
- ❌ Untraceable answers (no source chunk references)

---

## How to Use This Specification Package

### For Product Managers

**Read first:**
1. PROTOTYPE_OVERVIEW.md (this document)
2. PROTOTYPE_SCOPE.md (in/out of scope)
3. PROTOTYPE_LIMITATIONS.md (current limitations)
4. PROTOTYPE_SUCCESS_CRITERIA.md (what counts as success)

**Focus on:** What the prototype will demonstrate, what it won't do, readiness for next phase

---

### For Engineering Teams

**Read first:**
1. PROTOTYPE_OVERVIEW.md (this document)
2. PROTOTYPE_DATA_SOURCES.md (which files to ingest)
3. PROTOTYPE_INGEST_SET.md (exact chunks to ingest)
4. PROTOTYPE_RETRIEVAL_FLOW.md (retrieval logic)
5. HANDOFF_TO_ENGINEERING.md (implementation guidance)

**Focus on:** What to build, which sources to use first, mandatory safeguards, validation criteria

---

### For QA and Testing Teams

**Read first:**
1. PROTOTYPE_OVERVIEW.md (this document)
2. PROTOTYPE_TEST_QUERIES.md (test question set)
3. INTERNAL_TESTING_PLAN.md (testing approach)
4. PROTOTYPE_SUCCESS_CRITERIA.md (pass/fail criteria)

**Focus on:** How to test, what to look for, failure modes, evidence collection

---

### For Compliance and Legal

**Read first:**
1. PROTOTYPE_OVERVIEW.md (this document)
2. PROTOTYPE_EXCLUSIONS.md (what prototype must not do)
3. PROTOTYPE_RESPONSE_BEHAVIOR.md (answer safety behavior)
4. PROTOTYPE_LIMITATIONS.md (current limitations)

**Focus on:** Safety guardrails, placeholder handling, disclaimers, limitation disclosures

---

## Relationship to Other Project Phases

### Past Work (Completed)

**Phase 1-11:** Knowledge Base development and hardening
- Built FAQ, Rules, Plans, Network, Mapping content
- Repaired inconsistencies and structural gaps
- Created ingestion-ready package (KB_PACK_V1)

**Phase 12:** RAG execution specification
- Defined ingestion sequencing, metadata rules, filtering strategies
- Created weight formula ensuring trust hierarchy
- Defined 5-phase rollout plan and deployment gates
- Output: RAG_EXECUTION_SPEC_V1 (13 documents)

---

### Current Work (This Phase)

**Phase 13:** Internal prototype specification
- Define first internal-only retrieval prototype
- Specify conservative answer behavior
- Create test query set
- Define success criteria and handoff to engineering
- Output: RAG_PROTOTYPE_SPEC_V1 (this package, 16 documents)

---

### Future Work (Next Phases)

**Phase 14 (Engineering):** Implement internal prototype
- Ingest FAQ+Rules+Mapping chunks (67 strong chunks)
- Implement retrieval logic with trust hierarchy
- Build simple internal testing interface (CLI or web)
- Run test queries and validate behavior

**Phase 15 (Testing):** Internal QA and validation
- Execute internal testing plan
- Collect evidence for Gate A approval
- Identify knowledge gaps and create improvement backlog
- Prepare for Phase B deployment readiness review

**Phase 16+:** Limited pilot (Phase C), real data replacement (Phase D), production hardening (Phase E)

---

## Document Control

**Filename:** PROTOTYPE_OVERVIEW.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Internal Use Only  

**Related Documents:**
- All specification files in RAG_PROTOTYPE_SPEC_V1/ (this directory)
- RAG_EXECUTION_SPEC_V1/ (13 documents: ingestion, filtering, weighting, phases, gates)
- RAG_POLICY_V1/ (8 documents: trust hierarchy, metadata, placeholder policy)
- KB_PACK_V1/ (87 chunks in 5 JSONL files: source knowledge base)

**Version History:**
- v1.0 (March 19, 2026): Initial specification for internal prototype

---

## Quick Start

**If you're new to this project:**

1. **Read this document first** to understand what the prototype is and why it exists
2. **Read PROTOTYPE_SCOPE.md** to understand in/out of scope boundaries
3. **Read PROTOTYPE_LIMITATIONS.md** to understand current limitations
4. **Choose your role path:**
   - Engineering → HANDOFF_TO_ENGINEERING.md
   - QA → INTERNAL_TESTING_PLAN.md
   - Product → PROTOTYPE_SUCCESS_CRITERIA.md
   - Compliance → PROTOTYPE_EXCLUSIONS.md

**If you're implementing the prototype:**

1. Read HANDOFF_TO_ENGINEERING.md for implementation roadmap
2. Read PROTOTYPE_DATA_SOURCES.md for source files to ingest
3. Read PROTOTYPE_RETRIEVAL_FLOW.md for retrieval logic
4. Read PROTOTYPE_RESPONSE_BEHAVIOR.md for answer safety rules
5. Review PROTOTYPE_TEST_QUERIES.md for validation test set

**If you're testing the prototype:**

1. Read INTERNAL_TESTING_PLAN.md for testing approach
2. Use PROTOTYPE_TEST_QUERIES.md for structured test queries
3. Check PROTOTYPE_SUCCESS_CRITERIA.md for pass/fail criteria
4. Report findings using categories defined in INTERNAL_TESTING_PLAN.md

---

**END OF PROTOTYPE OVERVIEW**

**Next Document:** [PROTOTYPE_SCOPE.md](PROTOTYPE_SCOPE.md) - Define in-scope and out-of-scope boundaries
