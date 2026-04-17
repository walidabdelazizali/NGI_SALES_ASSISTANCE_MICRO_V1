# Checkpoint: Remedy 02–06 Stable

**Date:** 2026-04-13
**Tag:** `checkpoint-remedy-02-to-06-stable`
**Test count:** 222 passed, 0 failed

---

## 1. Supported Scope

| Plan       | Status    | Key Differentiators |
|------------|-----------|---------------------|
| Remedy 02  | Supported | Baseline plan, GP referral required, 12 physio sessions, AED 7,500 drugs |
| Remedy 03  | Supported | Same structure as R02; telemedicine = ISA Assist only; optical = 25% discount only |
| Remedy 04  | Supported | GP referral required, same benefits structure as R02/R03 |
| Remedy 05  | Supported | **Direct Access to Specialist** (no GP referral), 12 physio sessions, AED 7,500 drugs |
| Remedy 06  | Supported | Direct Access to Specialist, **20 physio sessions**, **AED 10,000 drugs**, **Shingrix vaccine** |

## 2. Intentionally NOT Supported

- **Remedy 01** — not yet implemented; blocked at plan gate
- **Remedy 07+** — not yet implemented; blocked at plan gate
- Any plan number outside 02–06 returns "Plan not supported yet"

## 3. Key Plan-Specific Behavior Notes

### Remedy 02 (Baseline)
- Annual limit: AED 150,000
- GP referral required for specialist
- Physiotherapy: 12 sessions/year, 15% copay
- Prescribed drugs: AED 7,500/year
- Maternity waiting period: 12 months

### Remedy 03
- Same benefit structure as R02
- **Telemedicine:** NOT a standalone benefit — available under ISA Assist / travel assistance only
- **Optical:** 25% discount at HN Basic Plus network — discount-only, not insured coverage
- Maternity waiting period: Nil

### Remedy 04
- GP referral required for specialist consultation
- Benefits structure same as R02/R03
- Prescribed drugs: AED 7,500/year
- Maternity waiting period: Nil

### Remedy 05
- **Direct Access to Specialist** — no GP referral needed
- Physiotherapy: 12 sessions/year
- Prescribed drugs: AED 7,500/year
- Maternity waiting period: Nil
- Shingrix: NOT covered (returns "No answer found")

### Remedy 06 (Deltas from R05)
- Direct Access to Specialist (same as R05)
- **Physiotherapy: 20 sessions/year** (R05 = 12)
- **Prescribed drugs: AED 10,000/year** (R05 = AED 7,500)
- **Shingrix vaccine: Covered** (DHA eligibility criteria, Non-LSB Dubai visa members)
- Network: HN Basic Plus (OP restricted to clinics) with direct-access hospitals
- Maternity waiting period: Nil

## 4. Sensitive Routing Rules

| Rule | Location | Behavior |
|------|----------|----------|
| Plan gate | `plan_lookup.py` top | Only 02–06 accepted; all others → "Plan not supported yet" |
| Explicit plan detection | `plan_lookup.py` benefit_map | R06 checked first → R05 → R04 → R02 → R03 (order prevents shadowing) |
| Maternity WP filter | `plan_lookup.py` line ~253 | `target_plan` filter ensures requested plan's CSV row wins |
| Telemedicine routing | `ask_kb.py` section 3 | ISA Assist distinction; not standalone OP benefit |
| Optical routing | `plan_lookup.py` + `ask_kb.py` | Maps to `additional_benefits.csv`; discount-only note in response |
| Shingrix routing | `plan_lookup.py` + `ask_kb.py` | Maps to `preventive_benefits.csv`; only R06 has a data row |
| Benefit dispatch regex | `router.py` | `0[23456]` — must be updated when adding new plans |

## 5. Known Architectural Constraints

- **CSV-driven data model** — all plan/benefit/rule data lives in `data/` CSVs
- **No database** — lookups iterate CSV rows in-memory per query
- **Subprocess architecture** — Telegram bot calls `ask_kb.py` as a subprocess
- **Plan ordering matters** — CSV row order affects first-match; the maternity WP bug was caused by this
- **11 duplicated allowed_variants blocks** in `plan_lookup.py` — must all be updated in sync when adding plans
- **No dynamic plan discovery** — plan numbers are hardcoded in guards, regex patterns, and routing dicts

## 6. How to Run Tests

```bash
# Activate virtual environment
source NGI-ROBOT/.venv/Scripts/activate   # bash
# or
& NGI-ROBOT\.venv\Scripts\Activate.ps1    # PowerShell

# Run all tests
python -m pytest tests/ -v --tb=short

# Run specific test pack
python -m pytest tests/test_remedy06_acceptance_pack.py -v
python -m pytest tests/test_maternity_wp_plan_label.py -v
```

## 7. How to Run the Telegram Bot

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
python scripts/telegram_bot.py
```

Or use: `start_telegram_bot.bat`

## 8. How to Validate the System Manually

```bash
# Single query
python scripts/ask_kb.py "What is the annual limit for Remedy 06?"

# Key validation queries:
python scripts/ask_kb.py "What is the maternity waiting period for Remedy 05?"
# Expected: "Maternity waiting period for Remedy 05: Nil."

python scripts/ask_kb.py "Does Remedy 06 include Shingrix vaccine?"
# Expected: "Shingrix vaccine for Remedy 06: Covered for members satisfying DHA eligibility criteria..."

python scripts/ask_kb.py "How many physiotherapy sessions are covered for Remedy 06?"
# Expected: "...maximum 20 sessions per year..."

python scripts/ask_kb.py "What is the prescribed drugs cover for Remedy 06?"
# Expected: "...AED 10,000 per year..."
```

## 9. Recovery Instructions

If future work causes regression or corruption:

```bash
# Return to this checkpoint
git checkout checkpoint-remedy-02-to-06-stable

# Or use the safety branch
git checkout backup/checkpoint-remedy-02-to-06-stable

# Verify integrity
python -m pytest tests/ -v --tb=short
# Expected: 222 passed, 0 failed
```

### Rollback Checklist
1. Check out the tag or branch above
2. Run the full test suite — must be 222 passed
3. Run the 20-query regression pack manually
4. Verify maternity WP returns correct plan labels for R05 and R06
5. If all green, the system is back to known-good state
