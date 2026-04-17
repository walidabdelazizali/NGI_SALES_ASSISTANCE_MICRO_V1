# FINAL STABILIZATION — Remedy 02 to 06 (Telegram)

**Date:** 2025-07-27  
**Previous checkpoint:** `checkpoint-remedy-02-06-conversational-hotfix-3272465`  
**This checkpoint tag:** `stabilized-remedy-02-to-06-telegram`  

---

## Scope

Final stabilization patch covering 7 known issues identified during post-Telegram-rollout QA.

## Issues Addressed

| # | Issue | Root Cause | Resolution |
|---|-------|-----------|------------|
| 1 | Maternity WP collision — "maternity cover" returning WP data | Arabic WP variants incomplete | Fixed at commit `3272465`: added `فترة انتظار`, `مدة انتظار`, `انتظار الحمل` to WP detection |
| 2 | Prenatal plan leakage — R06 query returning R02 data | `plan_lookup.py` lacked `target_plan` filter on prenatal/newborn | Fixed at commit `3272465`: target_plan filter added |
| 3 | Specialist referral routing — Arabic/English GP queries missing | `rule_patterns` had narrow keyword list | Fixed at commit `3272465`: 7 new terms added including `دخول مباشر`, `specialist` |
| 4 | Network membership vs summary — provider queries collapsing to plan lookup | Narrow regex `is X in the network` missed many phrasings | Fixed in this patch: data-driven provider detection using CSV-loaded names/aliases + broad intent phrases |
| 5 | Conservative network safety — unknown providers not flagged | Already handled by `network_lookup.py` "not confirmed" response | No change needed; verified working |
| 6 | Vaccine queries — influenza/Shingrix routing | Missing `benefit_patterns` and `benefit_map` entries | Fixed at commit `3272465`: influenza/pneumococcal/generic entries added |
| 7 | Unsupported plan safety — Remedy 07 returning data from other plans | Plan extraction already returns "No answer found" for unknown plans | No change needed; verified working |

## Files Changed (this patch, since `3272465`)

| File | Changes |
|------|---------|
| `scripts/ask_kb.py` | Replaced narrow regex-based provider detection with data-driven approach: loads provider names/aliases from CSV, checks substring + 2-word prefix matching, broad intent phrase list (EN + AR + Arabizi) |
| `src/network_lookup.py` | Added Arabizi direct billing terms (`ديركت بيلنج`, `ديرکت بيلنج`, `direct bill`) |
| `tests/test_provider_network_routing.py` | **NEW** — 19 tests in 7 classes covering provider routing |
| `tests/test_final_stabilization_regression.py` | **NEW** — 24 tests in 6 classes covering all 7 stabilization items (A-F) |

## Intentionally Unchanged

- `src/router.py` — routing logic is correct; no changes needed
- `src/plan_lookup.py` — already fixed at `3272465`
- All existing test files — no modifications to prior tests

## Test Evidence

```
279 passed in 37.26s
```

**Breakdown:**
- 236 tests — existing (from prior checkpoints)
- 19 tests — provider network routing pack
- 24 tests — final stabilization regression pack

## Test Categories (Final Stabilization Regression Pack)

| Category | Tests | Description |
|----------|-------|-------------|
| A) WP Disambiguation | 5 | Maternity WP vs maternity cover/limit, Arabic WP variant |
| B) Plan Leakage | 3 | Prenatal R04/R05/R06 must not mention other plans |
| C) Specialist Referral | 6 | GP referral R04, direct access R05/R06, Arabic R04/R05/R06 |
| D) Provider Network | 5 | Aster R03-R06 → [NETWORK], Cleveland R05 → "not confirmed" |
| E) Vaccine Handling | 3 | Influenza R04, Shingrix R06 covered, Shingrix R05 not listed |
| F) Unsupported Plan | 2 | Remedy 07 + Remedy 99 → "No answer found" |

## Sample CLI Outputs

```
Q: What is the maternity waiting period for Remedy 04?
A: [PLAN] Maternity waiting period for Remedy 04: Nil.

Q: Does Remedy 04 include maternity?
A: [PLAN] Maternity for Remedy 04: Maternity covered up to AED 10,000.

Q: What is the prenatal services cover for Remedy 06?
A: [PLAN] Prenatal for Remedy 06: ...  (no R02 leakage)

Q: Is Aster Hospital Qusais in the network for Remedy 03?
A: [NETWORK] Aster Hospital Qusais is in the HN Basic Plus network...

Q: Is Cleveland Clinic Abu Dhabi in the network for Remedy 05?
A: [NETWORK] Cleveland Clinic Abu Dhabi is not confirmed in the network.

Q: Does Remedy 04 include influenza vaccine?
A: [PLAN] Influenza vaccine for Remedy 04: Covered.

Q: What is the annual limit for Remedy 07?
A: No answer found.
```

## Known Limitations

1. **Remedy 01** queries may fall through to Remedy 02 data via maternity WP routing (WP keyword match before plan validation). Standard plan lookup correctly returns "No answer found" for non-existent plans.
2. Provider detection relies on CSV data — new providers must be added to `data/networks/provider_network_master.csv` and `data/networks/provider_aliases.csv`.

## Rollback

```bash
git checkout checkpoint-remedy-02-06-conversational-hotfix-3272465
```
