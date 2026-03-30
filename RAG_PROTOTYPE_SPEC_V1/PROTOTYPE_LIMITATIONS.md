# Prototype Limitations

**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Phase 1  

---

## Purpose

This document explicitly documents **the current limitations of the Phase 1 internal RAG prototype**. These limitations are **intentional by design** for internal testing and will be addressed in future phases.

Understanding these limitations is critical for:
1. **Setting appropriate expectations** with internal testers
2. **Preventing scope creep** during Phase 1
3. **Planning Phase 2+ enhancements**
4. **Understanding what the prototype can and cannot do**

---

## Limitation Categories

Limitations are organized into **7 categories**:

1. **Data Limitations** - What knowledge is missing or incomplete
2. **Operational Limitations** - What operations are not supported
3. **Technical Limitations** - What technology capabilities are absent
4. **Integration Limitations** - What systems are not connected
5. **User Experience Limitations** - What UX features are missing
6. **Performance Limitations** - What performance characteristics are not optimized
7. **Safety Limitations** - What safety validations are not complete

---

## Category 1: Data Limitations

### Limitation 1.1: Plan Layer is Placeholder-Only

**Current State:**
- **ALL 10 Plan chunks in plans_chunks.jsonl are placeholders** (status="Pending Detail")
- No real insurance product data ingested
- Plan benefit details, coverage limits, cost-sharing amounts, eligibility rules are NOT real
- All plan chunks marked `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`

**Impact:**
- ❌ Prototype CANNOT provide accurate plan-specific benefit details
- ❌ Prototype CANNOT compare real plans
- ❌ Prototype CANNOT state plan deductibles, copays, coinsurance, OOP max as facts
- ✅ Prototype CAN recognize plan names (Basic Family Plan, Premium Individual Plan, etc.)
- ✅ Prototype CAN provide general benefit guidance from FAQ/Rules
- ✅ Prototype MUST add mandatory disclaimers for any plan-specific question

**Workaround for Phase 1:**
- All plan-specific queries receive general guidance from FAQ/Rules
- Placeholder plan names recognized for context but details NOT stated
- Mandatory disclaimer directs to policy documents or customer service

**Resolution Timeline:**
- **Phase 2 (6 months):** Ingest real plan data from approved insurance products
- **Phase 2:** Replace placeholders with actual plan benefits, costs, eligibility rules
- **Phase 2:** Implement enhanced plan-specific retrieval and answering

---

### Limitation 1.2: Network Layer is Placeholder-Only

**Current State:**
- **ALL 10 Network chunks in network_chunks.jsonl are placeholders** (status="Pending Detail")
- No real provider directory data ingested
- Provider contracts, network status, facility agreements are NOT real
- All network chunks marked `is_placeholder=TRUE`, `safe_for_client_direct_use=FALSE`

**Impact:**
- ❌ Prototype CANNOT confirm provider network status
- ❌ Prototype CANNOT confirm facility network status
- ❌ Prototype CANNOT list in-network providers for a specialty or location
- ❌ Prototype CANNOT state contracted rates or provider tiers
- ✅ Prototype CAN recognize provider/facility names (Dr. Ahmed, Dubai Medical Center, etc.)
- ✅ Prototype CAN explain network verification process from FAQ
- ✅ Prototype CAN explain in-network vs out-of-network concepts
- ✅ Prototype MUST add mandatory network verification disclaimers

**Workaround for Phase 1:**
- All network queries receive verification process guidance
- Placeholder provider/facility names recognized but status NOT confirmed
- Mandatory disclaimer directs to customer service, online directory, or provider's office

**Resolution Timeline:**
- **Phase 3 (3 months after Phase 2):** Ingest real network data from provider contracts
- **Phase 3:** Implement provider directory search functionality
- **Phase 3:** Real-time or near-real-time network status validation

---

### Limitation 1.3: No Live Provider Directory Integration

**Current State:**
- Prototype does not connect to live provider directory API
- Network data (if present) would be static snapshot, not real-time

**Impact:**
- ❌ Prototype CANNOT provide up-to-date provider network status changes
- ❌ Prototype CANNOT search providers by specialty, location, insurance plan
- ❌ Provider joins/departures not reflected

**Workaround for Phase 1:**
- Directs users to online provider directory or customer service for current network status

**Resolution Timeline:**
- **Phase 3+:** Integrate with live provider directory API
- **Phase 4+:** Enable semantic search "find cardiologist in Dubai accepting Basic Family Plan"

---

### Limitation 1.4: Support, System, and Process Questions Partially Modeled

**Current State:**
- Some operational/process FAQ present (claims filing, adding dependents, contacting support)
- Some process FAQ may have status="Pending Detail" (incomplete guidance)
- Not all member support scenarios covered

**Impact:**
- ❌ Some how-to questions lack complete step-by-step guidance
- ❌ FAQ-010 (prescription refills) may be "Pending Detail" - prototype adds operational disclaimer
- ❌ Some member portal operations not documented
- ✅ Common processes like claims filing (FAQ-009) covered
- ✅ Contact information (FAQ-018) provided

**Workaround for Phase 1:**
- Provides available guidance from FAQ/Rules
- Adds operational disclaimer when FAQ status="Pending Detail"
- Directs to customer service for detailed or personalized help

**Resolution Timeline:**
- **Phase 2-3:** Complete operational FAQ for all common member support scenarios
- **Phase 4+:** Integrate with member portal for real-time operational guidance

---

### Limitation 1.5: No Claims, Underwriting, or Account Data

**Current State:**
- Prototype is retrieval-only
- No connection to claims adjudication systems
- No connection to underwriting systems
- No connection to member account/enrollment systems

**Impact:**
- ❌ Prototype CANNOT answer "What's my claim status?"
- ❌ Prototype CANNOT answer "How much have I paid toward deductible?"
- ❌ Prototype CANNOT answer "Am I eligible for this plan?"
- ❌ Prototype CANNOT perform account operations (change address, add dependent, submit claim)
- ✅ Prototype CAN explain how to file a claim (process guidance)
- ✅ Prototype CAN explain enrollment eligibility rules generally

**Workaround for Phase 1:**
- Account-specific queries trigger Tier 5 safe fallback
- Directs to member portal or customer service for account data

**Resolution Timeline:**
- **Phase 5+:** Consider read-only integration with claims/account systems for authenticated internal users
- **Production (Phase 7+):** Authenticated member access to personalized account data

---

## Category 2: Operational Limitations

### Limitation 2.1: Internal Testing Only - NOT Customer-Facing

**Current State:**
- Prototype is **internal tool for knowledge engineers, product team, and compliance team**
- NO customer access
- NO customer service representative access
- NO production deployment

**Impact:**
- ❌ Customers CANNOT use prototype to get insurance information
- ❌ Customer service reps CANNOT use prototype to answer customer questions
- ✅ Internal team CAN test retrieval quality
- ✅ Internal team CAN validate KB quality
- ✅ Internal team CAN identify FAQ/Rules gaps

**Rationale:**
- Placeholder plans/network data not suitable for customer-facing use (legal liability)
- Retrieval quality not validated for customer expectations
- Answer behavior not tested with real users
- Safety rules not validated for production use

**Resolution Timeline:**
- **Phase 2-3:** Continue internal testing with real plan/network data
- **Phase 4-5:** Enhanced retrieval, answer generation, safety validation
- **Phase 6:** Controlled customer pilot with select users
- **Phase 7:** Production customer-facing deployment

---

### Limitation 2.2: No Automation or Workflow Integration

**Current State:**
- Prototype is standalone retrieval system
- No integration with n8n workflows
- No integration with Telegram chatbot
- No integration with member portal
- No integration with customer service ticketing systems

**Impact:**
- ❌ No automated responses to customer inquiries
- ❌ No workflow-triggered knowledge retrieval
- ❌ No chatbot conversation support
- ❌ Manual query input and response review

**Workaround for Phase 1:**
- Manual test query execution
- Human review of all responses

**Resolution Timeline:**
- **Phase 5:** API development for external system integration
- **Phase 6:** Pilot integration with customer service tools
- **Phase 7:** Full automation and workflow integration

---

### Limitation 2.3: No Real-Time Validation or Data Freshness

**Current State:**
- KB data is static snapshot (KB_PACK_V1 from Phase 12)
- No real-time updates from policy systems, claims systems, provider contracts
- No data freshness monitoring or alerts

**Impact:**
- ❌ Policy changes not reflected until KB updated manually
- ❌ Provider network changes not reflected
- ❌ Regulatory changes not reflected
- ❌ No notification when KB data becomes stale

**Workaround for Phase 1:**
- Manual KB updates as needed
- Disclaimers direct users to verify current information

**Resolution Timeline:**
- **Phase 4:** Implement KB update pipeline for policy/benefit changes
- **Phase 5:** Near-real-time provider directory sync
- **Phase 6+:** Automated data freshness monitoring and alerts

---

## Category 3: Technical Limitations

### Limitation 3.1: No Prescribed Technology Stack

**Current State:**
- Specification is technology-agnostic
- NO embedding model specified (OpenAI, Cohere, open-source, etc.)
- NO vector database specified (Pinecone, Weaviate, pgvector, Chroma, etc.)
- NO RAG framework specified (LlamaIndex, LangChain, Haystack, custom, etc.)
- NO answer generation approach specified (templates, LLMs, hybrid)

**Impact:**
- ✅ Implementation teams have flexibility to choose best-fit tools
- ⚠️ Performance characteristics (latency, accuracy) unknown until implemented
- ⚠️ Infrastructure requirements (cost, scaling) unknown until implemented

**Rationale:**
- Phase 1 is specification layer, intentionally technology-neutral
- Different deployment environments may prefer different tools
- Allows engineering teams to leverage existing infrastructure

**Resolution Timeline:**
- **During Implementation:** Engineering team selects and tests technology stack
- **Phase 2+:** Technology choices may evolve based on performance and cost

---

### Limitation 3.2: Semantic Search Only (No Hybrid Retrieval)

**Current State:**
- Specification assumes semantic vector search
- No BM25 or keyword search
- No hybrid retrieval (semantic + keyword)
- No re-ranking

**Impact:**
- ❌ May miss exact keyword matches if semantically distant
- ❌ Medical term exact matches may be challenging
- ❌ Policy document section references (e.g., "Section 5.2") may not retrieve well
- ✅ Semantic search handles conceptual queries well

**Workaround for Phase 1:**
- Test semantic search performance
- Document cases where exact keyword matching would improve results

**Resolution Timeline:**
- **Phase 4:** Implement hybrid retrieval (semantic + BM25)
- **Phase 4:** Implement re-ranking for improved relevance
- **Phase 5:** Advanced retrieval techniques (query expansion, multi-vector)

---

### Limitation 3.3: No Advanced Answer Generation

**Current State:**
- Specification does not prescribe LLM-based answer generation
- Answers may be template-based or chunk concatenation
- No conversational context (single-turn queries only)
- No answer personalization

**Impact:**
- ❌ Answers may be less fluent or natural than LLM-generated answers
- ❌ No conversational memory ("What did I just ask about?")
- ❌ No personalization based on user role, history, or preferences
- ✅ Simpler implementation for Phase 1
- ✅ More predictable and controllable answers

**Workaround for Phase 1:**
- Use FAQ language for customer-friendly wording
- Template-based or chunk-based answers acceptable for internal testing

**Resolution Timeline:**
- **Phase 5:** Implement LLM-based answer generation with safety guardrails
- **Phase 5:** Conversational context and memory
- **Phase 6:** Personalization based on user profile

---

### Limitation 3.4: No Performance Optimization

**Current State:**
- No performance requirements specified (latency, throughput)
- No caching strategy
- No query optimization
- No index optimization

**Impact:**
- ⚠️ Retrieval latency unknown until implemented (could be 100ms or 2000ms)
- ⚠️ Concurrency unknown (how many simultaneous queries?)
- ⚠️ Cost per query unknown (embedding model, vector DB costs)

**Workaround for Phase 1:**
- Internal testing does not require production-level performance
- Measure baseline performance during implementation

**Resolution Timeline:**
- **Phase 4:** Performance benchmarking and optimization
- **Phase 5:** Caching, query optimization, index tuning
- **Phase 6:** Production-level SLAs (e.g., p95 latency <500ms)

---

## Category 4: Integration Limitations

### Limitation 4.1: No Policy Administration System Integration

**Current State:**
- KB built manually from policy documents and subject matter expert input
- No live connection to Policy Administration System (PAS)
- Policy changes not automatically reflected in KB

**Impact:**
- ❌ Policy updates require manual KB updates
- ❌ No real-time policy validation
- ❌ Policy effective dates not automatically tracked

**Workaround for Phase 1:**
- Manual KB updates when policies change
- Version control for KB updates

**Resolution Timeline:**
- **Phase 4:** Implement policy change monitoring and KB update pipeline
- **Phase 5:** Semi-automated policy ingestion from PAS

---

### Limitation 4.2: No Claims System Integration

**Current State:**
- No connection to claims adjudication system
- No access to claims status, history, or payment information

**Impact:**
- ❌ Cannot answer account-specific claims questions
- ✅ CAN explain claims process generally

**Workaround for Phase 1:**
- General claims process guidance from FAQ
- Direct users to claims department for specific claim status

**Resolution Timeline:**
- **Phase 5+:** Read-only integration with claims system for authenticated users

---

### Limitation 4.3: No Member Portal or CRM Integration

**Current State:**
- No connection to member portal
- No connection to CRM or customer service systems
- No ability to create tickets, escalations, or follow-ups

**Impact:**
- ❌ Cannot perform member portal operations
- ❌ Cannot access member profile or preferences
- ❌ Cannot create support tickets

**Workaround for Phase 1:**
- Directs users to member portal or customer service for account operations

**Resolution Timeline:**
- **Phase 6:** API integration with member portal and CRM
- **Phase 7:** Seamless handoff between RAG system and human support

---

## Category 5: User Experience Limitations

### Limitation 5.1: No User Interface

**Current State:**
- Prototype is backend retrieval system only
- No web UI, mobile app, or chatbot interface
- Query input and response review likely via API or command-line testing tools

**Impact:**
- ❌ No visual/graphical user interface for testers
- ❌ No chat-like conversational experience
- ✅ Focus on retrieval and answer quality, not UX

**Rationale:**
- Phase 1 focuses on knowledge retrieval and safety validation
- UI development postponed until retrieval quality validated

**Resolution Timeline:**
- **Phase 5:** Internal testing UI for knowledge engineers
- **Phase 6:** Pilot customer-facing chat interface
- **Phase 7:** Production web/mobile UI

---

### Limitation 5.2: No Conversational Context

**Current State:**
- Each query treated as independent, single-turn
- No memory of previous queries or conversation history
- No follow-up question handling ("What about maternity?" without context)

**Impact:**
- ❌ Cannot handle follow-up questions without full context
- ❌ Cannot maintain conversation flow
- ✅ Simpler implementation for Phase 1

**Workaround for Phase 1:**
- Testers provide full context in each query
- Query reformulation if needed

**Resolution Timeline:**
- **Phase 5:** Conversational context and memory
- **Phase 6:** Multi-turn conversation support

---

### Limitation 5.3: No Personalization

**Current State:**
- Answers are generic, not personalized to user role, plan, or history
- No user authentication or profile
- All users receive same answer to same query

**Impact:**
- ❌ Cannot tailor answers to user's specific plan
- ❌ Cannot adjust complexity based on user knowledge level
- ❌ Cannot prioritize based on user history or preferences
- ✅ Consistent answers across all users (good for internal testing)

**Workaround for Phase 1:**
- Generic answers acceptable for internal testing
- Plan-specific details require manual verification anyway (placeholders)

**Resolution Timeline:**
- **Phase 6:** User authentication and profile
- **Phase 6:** Plan-aware personalization
- **Phase 7:** Learning from user interactions and preferences

---

## Category 6: Performance Limitations

### Limitation 6.1: No Performance SLAs

**Current State:**
- No specified latency requirements
- No specified throughput (queries per second)
- No specified availability (uptime %)

**Impact:**
- ⚠️ Performance characteristics unknown until implementation
- ⚠️ Scalability unknown
- ✅ Sufficient for internal testing (low query volume, no real-time requirements)

**Rationale:**
- Phase 1 internal testing does not require production-level performance
- Baseline performance measured during implementation

**Resolution Timeline:**
- **Phase 4:** Performance benchmarking and requirements
- **Phase 6:** Production SLAs defined (e.g., p95 < 500ms, 99.9% uptime)
- **Phase 7:** Production monitoring and alerting

---

### Limitation 6.2: Unknown Accuracy/Relevance Metrics

**Current State:**
- Baseline accuracy/relevance unknown until testing
- No historical benchmark for comparison
- Success criteria defined but not yet measured

**Impact:**
- ⚠️ FAQ retrieval relevance target: ≥85% (untested)
- ⚠️ Rules retrieval relevance target: ≥80% (untested)
- ✅ Clear success criteria defined in PROTOTYPE_SUCCESS_CRITERIA.md
- ✅ Test queries defined in PROTOTYPE_TEST_QUERIES.md

**Workaround for Phase 1:**
- Run test queries and measure baseline performance
- Iterate on retrieval configuration if targets not met

**Resolution Timeline:**
- **Weeks 2-3 of Phase 1:** Baseline measurement
- **Phase 2+:** Continuous accuracy monitoring and improvement

---

## Category 7: Safety Limitations

### Limitation 7.1: Safety Rules Not Production-Validated

**Current State:**
- Safety rules (placeholder downweighting, mandatory disclaimers, violation detection) defined in specification
- NOT yet validated with real implementation
- NOT yet tested with real users or edge cases

**Impact:**
- ⚠️ Unknown if safety rules are sufficient for all scenarios
- ⚠️ Unknown if detection mechanisms catch all violations
- ✅ Conservative safety approach (reject uncertain rather than overstate)

**Rationale:**
- Phase 1 internal testing will validate safety rules
- Real user testing (Phase 6+) will identify additional edge cases

**Resolution Timeline:**
- **Weeks 2-3 of Phase 1:** Safety validation with test queries
- **Phase 2-3:** Enhanced safety rules based on testing findings
- **Phase 6:** Safety validation with pilot customer testing
- **Phase 7:** Production safety monitoring and alerting

---

### Limitation 7.2: Compliance and Legal Review Incomplete

**Current State:**
- Internal prototype specification
- NOT yet reviewed by legal counsel for customer-facing use
- NOT yet reviewed by regulatory compliance for insurance regulations
- NOT yet validated for HIPAA, data privacy, or other regulatory requirements

**Impact:**
- ❌ **NOT approved for customer-facing use**
- ❌ Compliance requirements for production unknown
- ✅ Sufficient for internal testing only

**Rationale:**
- Legal and compliance review postponed until customer-facing deployment planned (Phase 6+)
- Internal testing does not require full compliance validation

**Resolution Timeline:**
- **Phase 5:** Legal and compliance review of customer-facing prototype design
- **Phase 6:** Full compliance validation for pilot
- **Phase 7:** Production compliance certification

---

### Limitation 7.3: No Audit Trail or Logging at Scale

**Current State:**
- Traceability metadata defined in specification
- NOT yet implemented at scale
- Unknown if logging sufficient for audit, debugging, or regulatory requirements

**Impact:**
- ⚠️ Audit capabilities unknown until implementation
- ⚠️ Log storage and retention strategy undefined
- ✅ Metadata structure defined for traceability

**Workaround for Phase 1:**
- Manual test result recording
- Small query volume manageable with basic logging

**Resolution Timeline:**
- **Phase 4:** Implement structured logging and audit trail
- **Phase 5:** Log analytics and monitoring
- **Phase 7:** Compliance-grade audit trail for production

---

## Summary: What Prototype CAN and CANNOT Do

### ✅ Prototype CAN:
1. Retrieve relevant FAQ and Rules chunks for common insurance questions
2. Provide customer-friendly definitions and concepts from FAQ
3. Explain policy logic and reasoning from Rules
4. Recognize plan and provider names from placeholders (context only)
5. Add mandatory disclaimers for plan/network queries
6. Provide general benefit guidance and verification processes
7. Direct users to appropriate resources (policy documents, customer service, member portal)
8. Preserve full traceability (source chunks, confidence tiers, disclaimers applied)
9. Identify KB quality gaps and improvement opportunities
10. Serve as safe internal testing environment

### ❌ Prototype CANNOT:
1. Provide accurate plan-specific benefit details (placeholder data only)
2. Confirm provider or facility network status (placeholder data only)
3. State costs, deductibles, copays, coinsurance from plans (placeholder data only)
4. Answer account-specific questions (no account system integration)
5. Make claims adjudication decisions (no claims system integration)
6. Make underwriting or eligibility decisions (no underwriting system integration)
7. Perform account operations (no transactional capabilities)
8. Provide real-time data (static KB snapshot)
9. Serve customer-facing use cases (internal testing only)
10. Replace policy documents or qualified professionals (legal, compliance, medical)

---

## Managing Expectations

### For Internal Testers:
- ✅ Test retrieval quality and answer behavior
- ✅ Identify KB gaps and improvement opportunities
- ✅ Validate general insurance concept explanations
- ❌ Do NOT expect accurate plan-specific benefits (placeholders only)
- ❌ Do NOT expect network status confirmation (placeholders only)
- ❌ Do NOT use for customer-facing answers without further validation

### For Product Team:
- ✅ Validate Phase 1 scope and internal testing approach
- ✅ Identify Phase 2+ enhancement priorities
- ✅ Assess KB quality baseline
- ❌ Do NOT plan customer rollout until Phases 2-6 complete
- ❌ Do NOT commit to production timelines until real data ingested and tested

### For Engineering Team:
- ✅ Implement per specification
- ✅ Measure baseline performance and accuracy
- ✅ Validate safety rule enforcement
- ❌ Do NOT optimize for production performance in Phase 1
- ❌ Do NOT build customer-facing features yet

### For Compliance Team:
- ✅ Review safety rules and disclaimers for internal use
- ✅ Identify compliance requirements for future customer-facing deployment
- ❌ Do NOT expect full compliance validation for Phase 1 (internal only)
- ❌ Do NOT approve customer-facing use until Phases 5-6 compliance review

---

## Document Control

**Filename:** PROTOTYPE_LIMITATIONS.md  
**Version:** 1.0  
**Date:** March 20, 2026  
**Status:** Internal Prototype Specification  

**Related Documents:**
- PROTOTYPE_OVERVIEW.md - Context and purpose
- PROTOTYPE_SCOPE.md - What's in/out of scope
- PROTOTYPE_SUCCESS_CRITERIA.md - Success metrics
- INTERNAL_TESTING_PLAN.md - Testing approach (next)
- HANDOFF_TO_ENGINEERING.md - Engineering handoff (next)

---

**END OF LIMITATIONS SPECIFICATION**
