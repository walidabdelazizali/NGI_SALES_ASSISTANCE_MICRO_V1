# BASELINE_V1_STATUS.md

## 1. What currently works
- CLI (`scripts/ask_kb.py`) routes queries using normalized logic for both English and mixed Arabic/English phrasing.
- Structured lookups for:
  - Annual limit
  - Maternity
  - Area of coverage
  - Pre-existing rule
  - Network provider existence
- FAQ fallback for common questions.
- All tests in `tests/` pass (as of baseline freeze).

## 2. What is currently validated
- Plan core queries (annual limit, maternity, area of coverage, pre-existing, network existence) for Remedy 02.
- FAQ fallback for some process/definition queries.
- Output labels: [PLAN], [NETWORK], [FAQ], and 'No answer found.'
- CLI normalization for mixed Arabic/English phrasing.

## 3. What is not guaranteed yet
- Full coverage for all plan variants (e.g., Remedy 04, Remedy 05, etc.).
- Benefits & exclusions (inpatient, outpatient, dental, optical, etc.)
- Provider-to-plan mapping, city-based lookups, provider type lookups.
- Robust handling of all spelling/alias/variant cases.
- Full FAQ/terms & conditions coverage.
- Owner-facing validation dataset.

## 4. Exact commands to run

```bash
# Run all tests
python -m pytest

# Example CLI queries (from repo root or NGI_SALES_ASSISTANCE_MICRO_V1/):
python scripts/ask_kb.py "What is the annual limit for Remedy 02?"
python scripts/ask_kb.py "Does Remedy 02 include maternity?"
python scripts/ask_kb.py "What is the area of coverage for Remedy 02?"
python scripts/ask_kb.py "Is Aster Qusais in the network?"
python scripts/ask_kb.py "ما هو annual limit لخطة ريميدي 02؟"
python scripts/ask_kb.py "هل ريمدي ٢ فيها حمل؟"
```

## 5. Example successful CLI queries
- What is the annual limit for Remedy 02?
- Does Remedy 02 include maternity?
- What is the area of coverage for Remedy 02?
- Is Aster Qusais in the network?
- ما هو annual limit لخطة ريميدي 02؟
- هل ريمدي ٢ فيها حمل؟

## 6. Known limitations
- Only Remedy 02 is fully validated for plan core queries.
- No robust support for exclusions, approvals, or detailed benefits.
- No city-based or provider-type network queries.
- FAQ/terms coverage is limited to seeded examples.
- No owner-facing validation dataset yet.

## 7. Recommended next expansion areas
- Add owner-facing validation dataset and tests.
- Expand plan core coverage to more plans (Remedy 04, 05, etc.).
- Add support for benefits/exclusions (inpatient, outpatient, dental, etc.).
- Improve provider/alias/city lookups.
- Expand FAQ/terms coverage.
- Add more robust normalization for spelling/alias/variant cases.
