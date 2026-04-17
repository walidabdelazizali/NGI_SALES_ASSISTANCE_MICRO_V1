#!/usr/bin/env python
"""Remedy 05 — Phase 4A Validation Pack (English + Arabic).

Runs via ask_kb.py CLI and checks all core fields plus safety gates.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "ask_kb.py"
PASS = 0
FAIL = 0


def _ask(q: str) -> str:
    r = subprocess.run([sys.executable, str(SCRIPT), q], capture_output=True, text=True)
    return r.stdout.strip()


def _check(label: str, query: str, *expected_substrings: str, forbidden: list[str] | None = None):
    global PASS, FAIL
    out = _ask(query)
    ok = all(s.lower() in out.lower() for s in expected_substrings)
    if forbidden:
        ok = ok and all(s.lower() not in out.lower() for s in forbidden)
    status = "PASS" if ok else "FAIL"
    if status == "FAIL":
        FAIL += 1
    else:
        PASS += 1
    print(f"[{status}] {label}")
    if status == "FAIL":
        print(f"       Query: {query}")
        print(f"       Output: {out[:200]}")
        print(f"       Expected: {expected_substrings}")
    return ok


if __name__ == "__main__":
    print("=" * 70)
    print("REMEDY 05 — Phase 4A Validation Pack")
    print("=" * 70)

    # ── English core fields ──
    print("\n── English Core Fields ──")
    _check("EN: Annual Limit",
           "What is the annual limit for Remedy 05?",
           "150,000", "Remedy 05")

    _check("EN: Area of Coverage",
           "What is the area of coverage for Remedy 05?",
           "Remedy 05", "UAE")

    _check("EN: Copayment",
           "What is the copay for Remedy 05?",
           "Remedy 05", "20%")

    _check("EN: Provider Network",
           "What is the provider network for Remedy 05?",
           "Remedy 05", "HN Basic Plus")

    _check("EN: Maternity",
           "Does Remedy 05 include maternity?",
           "Remedy 05", "10,000")

    _check("EN: Reimbursement (inside UAE)",
           "What is the reimbursement policy inside UAE for Remedy 05?",
           "Remedy 05", "reimbursement")

    _check("EN: Telemedicine",
           "Does Remedy 05 include telemedicine?",
           "Remedy 05")

    _check("EN: Outpatient Coverage",
           "What outpatient coverage does Remedy 05 have?",
           "General OP")

    _check("EN: Inpatient Coverage",
           "What inpatient coverage does Remedy 05 have?",
           "IP")

    _check("EN: Emergency Coverage",
           "What emergency coverage does Remedy 05 have?",
           "Covered")

    _check("EN: Pharmacy",
           "What pharmacy coverage does Remedy 05 have?",
           "7,500")

    _check("EN: Wellness",
           "Does Remedy 05 include wellness?",
           "checkup")

    _check("EN: Deductible",
           "What is the deductible for Remedy 05?",
           "1,000")

    _check("EN: Benefits overview",
           "What are the benefits of Remedy 05?",
           "Overview", "Annual Limit", "Copayment")

    # ── Arabic core fields ──
    print("\n── Arabic Core Fields ──")
    _check("AR: Annual Limit",
           "كم الحد السنوي لريمدي 05؟",
           "150,000")

    _check("AR: Copayment",
           "كم الكوباي لريمدي 05؟",
           "20%")

    _check("AR: Area of Coverage",
           "شو منطقة التغطية لريمدي 05؟",
           "UAE")

    _check("AR: Maternity",
           "هل ريمدي 05 يغطي الأمومة؟",
           "10,000")

    _check("AR: Benefits overview",
           "شو فوائد ريمدي 05؟",
           "Overview", "Annual Limit")

    # ── Network / Direct Billing ──
    print("\n── Network & Direct Billing ──")
    _check("EN: Aster in network R05",
           "Is Aster Hospital Qusais in the network for Remedy 05?",
           "[NETWORK]", "aster hospital qusais")

    _check("EN: Cleveland not confirmed R05",
           "Is Cleveland Clinic Abu Dhabi in the network for Remedy 05?",
           "[NETWORK]", "not confirmed")

    _check("EN: Direct billing Aster R05",
           "Does Aster Hospital Qusais offer direct billing for Remedy 05?",
           "[NETWORK]")

    # ── Safety gates ──
    print("\n── Safety Gates ──")
    _check("GATE: R06 still works",
           "What is the annual limit for Remedy 06?",
           "150,000", "Remedy 06")

    _check("GATE: Prime still blocked",
           "What is the annual limit for Prime 1?",
           "No answer found.")

    _check("GATE: R02 still works",
           "What is the annual limit for Remedy 02?",
           "150,000", "Remedy 02")

    _check("GATE: R03 still works",
           "What is the annual limit for Remedy 03?",
           "150,000", "Remedy 03")

    _check("GATE: R04 still works",
           "What is the annual limit for Remedy 04?",
           "150,000", "Remedy 04")

    _check("GATE: Classic 2 still works",
           "What is the annual limit for Classic 2?",
           "Classic")

    # ── Summary ──
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"RESULTS: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("STATUS: ALL CHECKS PASSED — Remedy 05 Phase 4A validated")
    else:
        print("STATUS: FAILURES DETECTED — review above")
    print("=" * 70)
    sys.exit(1 if FAIL else 0)
