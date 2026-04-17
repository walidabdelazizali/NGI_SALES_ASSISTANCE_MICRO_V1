#!/usr/bin/env python
"""Phase 4D — Arabic Classic Alias + Anti-Wrong-Default Validation Pack.

Checks Arabic Classic queries resolve correctly and never misroute to Remedy 02.
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
        if forbidden:
            print(f"       Forbidden: {forbidden}")
    return ok


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 4D — Arabic Classic Alias Validation Pack")
    print("=" * 70)

    # ── Arabic Classic annual limit ──
    print("\n── Arabic Classic: Annual Limit ──")
    _check("AR: Classic 2 annual limit",
           "كم الحد السنوي لكلاسيك 2؟",
           "250,000", "classic",
           forbidden=["remedy 02", "remedy 03"])

    _check("AR: Classic 3 annual limit",
           "شو الحد السنوي خطة كلاسيك 3؟",
           "250,000", "classic",
           forbidden=["remedy"])

    _check("AR: Classic 4 annual limit",
           "كم الحد السنوي لبلان كلاسيك 4؟",
           "150,000", "classic",
           forbidden=["remedy"])

    _check("AR: Classic 1R annual limit",
           "كم الحد السنوي لكلاسيك 1r؟",
           "classic",
           forbidden=["remedy"])

    # ── Arabic Classic maternity (anti-wrong-default) ──
    print("\n── Arabic Classic: Maternity (anti-wrong-default) ──")
    _check("AR: Classic 2 maternity — not Remedy 02",
           "هل كلاسيك 2 تغطي الأمومة؟",
           "classic", "maternity",
           forbidden=["remedy 02"])

    _check("AR: Classic 3 maternity — not Remedy 02",
           "هل كلاسيك 3 تغطي الأمومة؟",
           "classic", "maternity",
           forbidden=["remedy 02"])

    _check("AR: Classic 4 maternity (حمل)",
           "هل كلاسيك 4 تغطي حمل؟",
           "classic",
           forbidden=["remedy 02"])

    # ── Arabic Classic area of coverage ──
    print("\n── Arabic Classic: Area of Coverage ──")
    _check("AR: Classic 2 area",
           "شو منطقة التغطية كلاسيك 2؟",
           "classic",
           forbidden=["remedy"])

    # ── English Classic (no regression) ──
    print("\n── English Classic (no regression) ──")
    _check("EN: Classic 2 annual limit",
           "What is the annual limit for Classic 2?",
           "250,000", "classic")

    _check("EN: Classic 2 maternity",
           "Does Classic 2 cover maternity?",
           "classic", "maternity")

    _check("EN: Classic 3 annual limit",
           "What is the annual limit for Classic 3?",
           "250,000", "classic")

    # ── Remedy (no regression) ──
    print("\n── Remedy (no regression) ──")
    _check("EN: Remedy 02 annual limit",
           "What is the annual limit for Remedy 02?",
           "150,000", "remedy 02")

    _check("EN: Remedy 05 maternity",
           "Does Remedy 05 include maternity?",
           "10,000", "remedy 05")

    _check("EN: Remedy 06 pharmacy",
           "What pharmacy coverage does Remedy 06 have?",
           "10,000", "remedy 06")

    _check("AR: Remedy 02 annual limit",
           "كم الحد السنوي لريمدي 02؟",
           "150,000")

    # ── Safety gates ──
    print("\n── Safety Gates ──")
    _check("GATE: Prime still blocked",
           "What is the annual limit for Prime 1?",
           "no answer found")

    _check("GATE: R07 still blocked",
           "What is the annual limit for Remedy 07?",
           "no answer found")

    # ── Summary ──
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"RESULTS: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("STATUS: ALL CHECKS PASSED — Phase 4D validated")
    else:
        print("STATUS: FAILURES DETECTED — review above")
    print("=" * 70)
    sys.exit(1 if FAIL else 0)
