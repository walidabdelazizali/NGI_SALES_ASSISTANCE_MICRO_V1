# RAG Prototype V1 - Scope Definition

**Version:** 1.0  
**Date:** March 19, 2026  
**Status:** Internal Testing Only  

---

## Purpose

This document defines **clear boundaries** for the internal RAG prototype:
- What is **in scope** for Phase 1 internal testing
- What is **out of scope** (intentionally excluded or postponed)
- What is **intentionally disabled** for safety/quality reasons
- What is **postponed** to later phases (C, D, E)

**Design Principle:** Start narrow and safe, expand gradually with validation at each phase.

---

## In Scope for Phase 1 Prototype

### ✅ Core Retrieval Capabilities

**1. FAQ Retrieval**
- **What:** Retrieve and present customer-facing FAQ explanations for common insurance concepts
- **Sources:** 20 FAQ chunks from `faq_chunks.jsonl`
- **Use cases:** General insurance questions (deductibles, copays, coverage concepts, claim types)
- **Confidence level:** HIGH - these are reviewed, customer-safe explanations
- **Answer style:** Direct, confident, customer-friendly language

**2. Rules Retrieval**
- **What:** Retrieve and apply policy rules and benefit logic
- **Sources:** 27 Rules chunks from `rules_chunks.jsonl`
- **Use cases:** Policy interpretation, benefit eligibility, rule-based reasoning
- **Confidence level:** HIGH - these are derived from policy documents
- **Answer style:** Policy-accurate, includes reasoning, may reference plan confirmation

**3. Mapping-Assisted Reasoning**
- **What:** Use mapping chunks to discover related FAQ/Rules content
- **Sources:** 20 Mapping chunks from `mapping_reference.jsonl`
- **Use cases:** Cross-topic navigation, finding related content, enriching answers with connected concepts
- **Confidence level:** MEDIUM - mappings provide context, not primary facts
- **Answer style:** Used for context only, never displayed directly to users

---

### ✅ Answer Generation Behavior

**4. Conservative Answer Behavior**
- **What:** Generate answers that prioritize truthfulness over completeness
- **Includes:**
  - Use FAQ wording when available (customer-safe language)
  - Use Rules for policy logic and interpretation
  - Explicit caution when plan-specific confirmation needed ("check your policy documents")
  - Explicit caution when network verification needed ("verify provider network status")
  - Honest refusal when prototype lacks evidence ("contact customer service")

**5. Traceability**
- **What:** Preserve complete source chain for every answer
- **Includes:**
  - `chunk_id` for every retrieved chunk
  - `source_file` and `source_id` for audit trail
  - Internal display of source references (for QA/validation)
  - "Show sources" capability for debugging

**6. Internal Testing Interface**
- **What:** Simple interface for internal team testing (CLI, web form, API endpoint - implementation choice)
- **Includes:**
  - Query input
  - Answer display
  - Source reference display (internal only)
  - Confidence level indicator
  - Caution/disclaimer display

---

### ✅ Safety and Governance

**7. Trust Hierarchy Enforcement**
- **What:** Ensure FAQ/Rules always dominate placeholder content
- **Includes:**
  - Weight formula implementation (FAQ/Rules 10x-12.5x higher than placeholders)
  - Placeholder downranking (placeholders score ≤0.1 even with high semantic match)
  - Filtering rules (optionally exclude placeholders from certain query types)

**8. Placeholder Guardrails**
- **What:** Prevent placeholders from creating false insurance certainty
- **Includes:**
  - Placeholder content never stated as confirmed product/provider facts
  - Placeholder content labeled internally as "⚠️ PLACEHOLDER - Not confirmed"
  - Placeholder-only scenarios trigger safe fallback ("contact customer service")
  - Plan-dependent questions require explicit confirmation disclaimers

**9. Internal Validation and Testing**
- **What:** Structured testing approach to validate prototype behavior
- **Includes:**
  - Test query set (20-30 queries across categories)
  - Success criteria (retrieval quality ≥85%, no false certainty, conservative answers)
  - Failure mode identification (placeholder leaks, missing disclaimers, untraceable answers)
  - Knowledge gap discovery (which FAQ/Rules need creation/improvement)

---

## Out of Scope for Phase 1 Prototype

### ❌ Deployment and Access

**1. Customer-Facing Deployment**
- **NOT included:** Direct customer access to prototype
- **Why:** Prototype is internal-only for validation, not production-ready
- **Alternative:** Internal team testing only (engineering, QA, product, compliance)
- **Future:** Phase C (limited pilot with 10-20 customers after internal validation)

**2. Production Infrastructure**
- **NOT included:** Production-grade hosting, high availability, disaster recovery
- **Why:** Internal testing doesn't require production SLAs
- **Alternative:** Development/staging environment sufficient
- **Future:** Phase E (production hardening)

**3. Public API or Bot Interface**
- **NOT included:** Public API endpoints, Telegram bot, WhatsApp integration
- **Why:** Premature for internal testing phase
- **Alternative:** Simple internal interface (CLI, web form, internal API)
- **Future:** Phase C+ after internal validation proves retrieval quality

---

### ❌ Data and Content

**4. Real Plan Data**
- **NOT included:** Confirmed plan benefits, coverage tables, plan pricing
- **Why:** Plans layer is placeholder-only (real data expected in 6 months)
- **Current state:** 10 placeholder plan chunks provide structural scaffolding only
- **Prototype behavior:** Recognize plan context (e.g., "Basic Family Plan") but never state placeholder benefits as confirmed facts
- **Alternative:** Use FAQ for general coverage concepts, defer plan-specific details to policy documents
- **Future:** Phase D (real data replacement)

**5. Live Provider Network Directory**
- **NOT included:** Real-time provider search, network status verification, appointment booking
- **Why:** Network layer is placeholder-only (real data expected in 3 months)
- **Current state:** 10 placeholder network chunks provide structural scaffolding only
- **Prototype behavior:** Recognize network questions but always require verification ("verify provider network status before appointment")
- **Alternative:** Use FAQ for general network concepts, defer provider-specific verification to official channels
- **Future:** Phase D (real data replacement)

**6. Operational Database Integration**
- **NOT included:** Member profiles, claims history, eligibility verification, real-time policy lookups
- **Why:** Prototype is knowledge base retrieval only, not operational system integration
- **Alternative:** Prototype assumes general/anonymous queries, doesn't personalize based on member data
- **Future:** Post-production (Phase E+) if personalization needed

---

### ❌ Automation and Operations

**7. Claims Adjudication**
- **NOT included:** Approve/deny claims, calculate claim payments, determine benefit eligibility for specific claims
- **Why:** Claims decisions require operational systems, underwriting rules, and human oversight - NOT knowledge base retrieval
- **Prototype behavior:** Can explain general claims concepts (FAQ), explain benefit rules (Rules), but must never automate approval/denial decisions
- **Alternative:** "Contact claims department for claim-specific decisions"
- **Future:** Out of scope permanently (claims operations remain in operational systems)

**8. Underwriting Decisions**
- **NOT included:** Approve/deny coverage, calculate premiums, assess risk
- **Why:** Underwriting requires operational systems, actuarial models, and regulatory compliance - NOT knowledge base retrieval
- **Prototype behavior:** Can explain general underwriting concepts (FAQ) but must never automate underwriting decisions
- **Alternative:** "Contact underwriting team for coverage decisions"
- **Future:** Out of scope permanently (underwriting remains in operational systems)

**9. Policy Document Generation**
- **NOT included:** Create/modify policy documents, generate certificates of insurance
- **Why:** Policy documents are legal/compliance artifacts requiring controlled authoring
- **Prototype behavior:** Can reference policy document requirements (Rules) but never generates official documents
- **Alternative:** "Policy documents are issued by [process]"
- **Future:** Out of scope permanently (policy generation remains in policy administration systems)

---

### ❌ Advanced Features

**10. Multi-Turn Conversation Memory**
- **NOT included:** Remember previous queries, maintain conversation context, personalize based on conversation history
- **Why:** Adds complexity, not needed for prototype validation
- **Prototype behavior:** Each query is independent (stateless)
- **Alternative:** Users can rephrase or provide full context in single query
- **Future:** Phase C+ if conversational UX needed

**11. Multi-Language Support**
- **NOT included:** Arabic, Hindi, Tagalog, or other language translations
- **Why:** Knowledge base is English-only currently
- **Prototype behavior:** English queries and answers only
- **Alternative:** N/A for internal testing (internal team is English-proficient)
- **Future:** Post-production if multi-language support becomes requirement

**12. Real-Time External Data Feeds**
- **NOT included:** Exchange rates, claim status updates, real-time eligibility checks
- **Why:** External integrations add complexity and dependencies
- **Prototype behavior:** Knowledge base retrieval only (static content)
- **Alternative:** Defer to operational systems for real-time data
- **Future:** Post-production if real-time integrations needed

---

## Intentionally Disabled Features

### 🔒 Disabled for Safety and Quality

**1. Placeholder Content as Primary Answer Source**
- **Status:** DISABLED by default for customer-facing query types
- **Why:** Placeholder content is structural scaffolding, not confirmed product/provider facts
- **Implementation:** 
  - Customer-facing query type: Filter out `is_placeholder=true` chunks entirely
  - Internal query type: Allow placeholders but label as "⚠️ PLACEHOLDER - Not confirmed"
- **Override:** Engineering can enable for testing, but must never deploy customer-facing with placeholders as primary sources

**2. High-Confidence Plan/Network Answers Without Disclaimers**
- **Status:** DISABLED - plan/network questions always require disclaimers
- **Why:** Plans and Network layers are placeholder-only, cannot provide confirmed facts
- **Implementation:**
  - Plan-dependent questions: Add "check your policy documents or contact customer service"
  - Network-dependent questions: Add "verify provider network status before scheduling appointment"
- **Override:** Phase D (real data replacement) can reduce disclaimers for confirmed data

**3. Direct Display of Mapping Chunk Text**
- **Status:** DISABLED - mapping chunks retrieved for context but text never shown to users
- **Why:** Mapping chunks are reference layer (chunk_id linkages), not user-friendly content
- **Implementation:** Use mappings to find related FAQ/Rules, then retrieve and display those instead
- **Override:** None - mappings are always context-only, never direct display

---

## Postponed to Later Phases

### 🕐 Phase C: Limited Pilot (4-6 weeks)

**Postponed capabilities:**
- Customer-facing deployment (10-20 pilot customers)
- Placeholder-aware retrieval with strict downranking
- Answer safety behavior for placeholder scenarios
- Real-time placeholder leak detection and alerting
- Compliance approval for pilot deployment

**Prerequisites:**
- Gate B approval (all Gate A criteria met + placeholder safety + answer safety + weight hierarchy)
- Internal testing feedback positive (2+ weeks)
- No critical bugs
- Compliance/legal sign-off

---

### 🕐 Phase D: Real Data Replacement (3-6 months)

**Postponed capabilities:**
- Real plan benefits from product finalization
- Real provider network from signed contracts
- Plan-specific answers with high confidence (fewer disclaimers)
- Network verification with confirmed status
- Placeholder deprecation and removal

**Prerequisites:**
- Real plan data obtained from product team (Timeline: 6 months)
- Real network data obtained from provider contracts (Timeline: 3 months)
- 7-step placeholder replacement process executed
- Replacement validation passed

---

### 🕐 Phase E: Production Hardening (Ongoing)

**Postponed capabilities:**
- Production-grade infrastructure and SLA
- Performance optimization (latency <500ms p95)
- Advanced monitoring and alerting
- Continuous content improvement loop
- User feedback collection and analysis
- Quarterly compliance audits

**Prerequisites:**
- Gate C approval (pilot success + safety/compliance re-validation + performance/scalability)
- Production infrastructure ready
- Rollback procedures tested
- 24/7 on-call established

---

## Scope Summary Table

| Capability | Phase 1 Prototype | Phase C Pilot | Phase D Real Data | Phase E Production |
|------------|-------------------|---------------|-------------------|-------------------|
| **FAQ Retrieval** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Rules Retrieval** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Mapping Support** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Placeholder Awareness** | ⚠️ Context only | ⚠️ With guardrails | ⚠️ Deprecating | ✅ Replaced with real data |
| **Customer-Facing** | ❌ Internal only | ⚠️ Limited pilot (10-20) | ⚠️ Controlled rollout | ✅ Full production |
| **Plan-Specific Answers** | ❌ Defer to policy docs | ⚠️ General + disclaimers | ✅ Real data available | ✅ High confidence |
| **Network Verification** | ❌ Defer to verification | ⚠️ General + disclaimers | ✅ Real data available | ✅ Confirmed status |
| **Claims Adjudication** | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **Underwriting** | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **Production Infrastructure** | ❌ Dev/staging only | ⚠️ Pilot environment | ⚠️ Pre-production | ✅ Production SLA |

**Legend:**
- ✅ Full capability available
- ⚠️ Limited/guarded capability
- ❌ Not available

---

## Scope Decision Rationale

### Why FAQ+Rules+Mapping First?

**Decision:** Phase 1 prototype uses 67 strong chunks (FAQ+Rules+Mapping) as primary sources, with 20 placeholders (Plans+Network) as optional weak context.

**Rationale:**
1. **High confidence:** FAQ and Rules are reviewed, policy-accurate, customer-safe
2. **Broad coverage:** FAQ covers most common insurance concepts, Rules cover policy logic
3. **Proven value:** 77% of knowledge base is strong content, sufficient for internal validation
4. **Low risk:** No placeholder liability if FAQ/Rules dominate retrieval
5. **Fast validation:** Can test retrieval quality without waiting for real plan/network data

**Alternative considered:** Wait for real plan/network data before building prototype
**Why rejected:** 6-month delay, loses opportunity for early validation and knowledge gap discovery

---

### Why Internal-Only First?

**Decision:** Phase 1 prototype is internal team testing only, no customer-facing deployment.

**Rationale:**
1. **Safety:** Validate retrieval quality before external exposure
2. **Iteration:** Rapid adjustments based on internal findings without customer impact
3. **Knowledge gaps:** Discover missing FAQ/Rules content without customer frustration
4. **Compliance:** Build evidence for compliance approval before pilot
5. **Risk mitigation:** Catch placeholder leaks or unsafe answers in controlled environment

**Alternative considered:** Deploy limited pilot immediately
**Why rejected:** Premature - need internal validation first to prove retrieval quality and placeholder handling

---

### Why No Claims/Underwriting Automation?

**Decision:** Prototype is knowledge base retrieval only, never automates operational decisions (claims, underwriting, approvals).

**Rationale:**
1. **Separation of concerns:** Knowledge retrieval ≠ operational decision-making
2. **Regulatory compliance:** Claims/underwriting require human oversight and regulatory controls
3. **Liability:** Automated decisions carry legal/financial liability requiring extensive validation
4. **Scope creep:** Operational automation is a separate (much larger) project
5. **Focus:** Prototype validates knowledge retrieval, not operational systems

**Alternative considered:** Include claims guidance that auto-approves simple claims
**Why rejected:** Legal liability too high, regulatory requirements too complex, out of scope

---

## Scope Change Process

### How to Request Scope Changes

If a capability is **out of scope** but stakeholders believe it should be **in scope**:

**Process:**
1. Document capability request with justification
2. Assess impact on timeline, complexity, risk
3. Identify prerequisites (e.g., data availability, compliance approval)
4. Determine appropriate phase (prototype vs pilot vs production)
5. Obtain approval from product, engineering, and compliance leads
6. Update scope document and related specs

**Approval required from:**
- Product lead (business justification)
- Engineering lead (feasibility and timeline)
- Compliance lead (regulatory/legal risk assessment)

---

### Scope Escalation

If there is disagreement about in-scope vs out-of-scope:

**Level 1:** Product and Engineering leads discuss and align  
**Level 2:** Add Compliance lead if regulatory/legal concerns  
**Level 3:** Escalate to senior leadership if unresolved  

**Final Authority:** Senior leadership (or designated decision maker)

---

## Document Control

**Filename:** PROTOTYPE_SCOPE.md  
**Version:** 1.0  
**Date:** March 19, 2026  
**Author:** Knowledge Engineering Team  
**Status:** Approved for Internal Use Only  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md (what this prototype is)
- PROTOTYPE_LIMITATIONS.md (current limitations)
- PROTOTYPE_EXCLUSIONS.md (what prototype must not do)
- RAG_EXECUTION_SPEC_V1/IMPLEMENTATION_PHASES.md (5-phase rollout plan)

---

**END OF PROTOTYPE SCOPE**

**Next Document:** [PROTOTYPE_DATA_SOURCES.md](PROTOTYPE_DATA_SOURCES.md) - Define which source files to use
