# COVERAGE_PACK_V1.md

## A. Plan Core
- **annual limit**
  - Sample: "What is the annual limit for Remedy 02?"
  - Supported: Yes (Remedy 02)
  - Patch needed: Expand to other plans
- **area of coverage**
  - Sample: "What is the area of coverage for Remedy 02?"
  - Supported: Yes (Remedy 02)
  - Patch needed: Expand to other plans
- **provider network**
  - Sample: "Is Aster Qusais in the network?"
  - Supported: Yes (Remedy 02)
  - Patch needed: Alias/city/type support
- **maternity**
  - Sample: "Does Remedy 02 include maternity?"
  - Supported: Yes (Remedy 02)
  - Patch needed: Expand to other plans, details
- **pre-existing conditions**
  - Sample: "Does Remedy 02 cover pre-existing conditions?"
  - Supported: Yes (Remedy 02, basic)
  - Patch needed: More detail, more plans
- **reimbursement**
  - Sample: "What is the reimbursement process for Remedy 02?"
  - Supported: No
  - Patch needed: Add FAQ/plan support
- **declaration rules**
  - Sample: "What are the declaration requirements for Remedy 02?"
  - Supported: Partial (FAQ only)
  - Patch needed: Structured plan support

## B. Benefits & Exclusions
- **inpatient**
  - Sample: "What inpatient benefits does Remedy 02 have?"
  - Supported: No
  - Patch needed: Add plan/FAQ support
- **outpatient**
  - Sample: "What outpatient coverage does Remedy 02 have?"
  - Supported: No
  - Patch needed: Add plan/FAQ support
- **dental**
  - Sample: "Does Remedy 02 include dental?"
  - Supported: No
  - Patch needed: Add plan/FAQ support
- **optical**
  - Sample: "Does Remedy 02 include optical?"
  - Supported: No
  - Patch needed: Add plan/FAQ support
- **maternity details**
  - Sample: "What is the maternity waiting period for Remedy 02?"
  - Supported: No (only basic maternity)
  - Patch needed: Add detail fields
- **exclusions**
  - Sample: "What are the exclusions for Remedy 02?"
  - Supported: No
  - Patch needed: Add exclusions data/FAQ
- **approvals / authorization**
  - Sample: "Is pre-authorization required for Remedy 02?"
  - Supported: No
  - Patch needed: Add plan/FAQ support

## C. Network Intelligence
- **provider exists or not**
  - Sample: "Is Aster Qusais in the network?"
  - Supported: Yes (Remedy 02)
  - Patch needed: Alias/city/type support
- **provider belongs to which plan**
  - Sample: "Which plans include Aster Qusais?"
  - Supported: No
  - Patch needed: Add reverse lookup
- **city-based lookups**
  - Sample: "Which providers are in Dubai?"
  - Supported: No
  - Patch needed: Add city data
- **provider type lookups**
  - Sample: "List all clinics in the network."
  - Supported: No
  - Patch needed: Add type data
- **alias / spelling variation cases**
  - Sample: "Is Aster Qussais in the network?"
  - Supported: Partial (basic normalization)
  - Patch needed: Expand alias/variant mapping

## D. FAQ / Training Reuse
- **simple definitions**
  - Sample: "What is a deductible?"
  - Supported: Partial (FAQ fallback)
  - Patch needed: Expand FAQ
- **process clarifications**
  - Sample: "How do I submit a claim?"
  - Supported: Partial (FAQ fallback)
  - Patch needed: Expand FAQ
- **customer-safe explanations**
  - Sample: "Explain pre-existing conditions."
  - Supported: Partial (FAQ fallback)
  - Patch needed: Expand FAQ
- **internal operational clarifications**
  - Sample: "What is the TAT for claim processing?"
  - Supported: Partial (FAQ fallback)
  - Patch needed: Expand FAQ

---

For each missing or partial area, a patch would require:
- Adding structured data or FAQ entries
- Expanding normalization/alias logic
- Adding new test cases
- Ensuring CLI routing supports the new category
