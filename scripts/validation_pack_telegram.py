"""
Telegram Bot Validation Pack — 30 high-value real-world questions.

Covers: annual limit, maternity, telemedicine, dental, area of coverage,
provider in network, direct billing, Arabic phrasing, unsupported plan
fallback, mixed Arabic-English phrasing.

Run:
    cd NGI_SALES_ASSISTANCE_MICRO_V1
    python scripts/validation_pack_telegram.py

Output: prints each question, the KB answer, and a PASS/FAIL tag based
on whether the answer is non-empty and not an error.
"""

import subprocess
import sys
from pathlib import Path

ASK_KB = Path(__file__).resolve().parent / "ask_kb.py"
PROJECT_ROOT = ASK_KB.parent.parent

QUESTIONS = [
    # --- Annual Limit ---
    {"q": "What is the annual limit for Remedy 02?", "expect_found": True, "tag": "annual_limit"},
    {"q": "What is the annual limit for Remedy 03?", "expect_found": True, "tag": "annual_limit"},
    {"q": "شو الحد السنوي لريمدي 02؟", "expect_found": True, "tag": "annual_limit_ar"},

    # --- Maternity ---
    {"q": "Does Remedy 02 include maternity?", "expect_found": True, "tag": "maternity"},
    {"q": "What is the maternity waiting period for Remedy 03?", "expect_found": True, "tag": "maternity"},
    {"q": "هل ريمدي 02 فيها تغطية حمل؟", "expect_found": True, "tag": "maternity_ar"},

    # --- Telemedicine ---
    {"q": "Does Remedy 02 include telemedicine?", "expect_found": True, "tag": "telemedicine"},
    {"q": "Is telemedicine covered under Remedy 04?", "expect_found": True, "tag": "telemedicine"},
    {"q": "هل تيليمديسن مغطى في ريمدي 02؟", "expect_found": True, "tag": "telemedicine_ar"},

    # --- Dental ---
    {"q": "Does Remedy 02 cover dental?", "expect_found": True, "tag": "dental"},
    {"q": "Does Remedy 03 include dental?", "expect_found": True, "tag": "dental"},
    {"q": "هل ريمدي 04 فيها أسنان؟", "expect_found": True, "tag": "dental_ar"},

    # --- Area of Coverage ---
    {"q": "What is the area of coverage for Remedy 02?", "expect_found": True, "tag": "area_of_coverage"},
    {"q": "What is the area of coverage for Classic 3?", "expect_found": True, "tag": "area_of_coverage"},

    # --- Provider in Network ---
    {"q": "Is Aster Hospital Qusais in the Remedy 02 network?", "expect_found": True, "tag": "provider_network"},
    {"q": "Is Burjeel Hospital in the network for Remedy 03?", "expect_found": True, "tag": "provider_network"},
    {"q": "هل أستر القصيص ضمن شبكة ريمدي 02؟", "expect_found": True, "tag": "provider_network_ar"},

    # --- Direct Billing ---
    {"q": "Does Remedy 02 offer direct billing?", "expect_found": True, "tag": "direct_billing"},
    {"q": "Does Aster Hospital Qusais offer direct billing for Remedy 02?", "expect_found": True, "tag": "direct_billing"},

    # --- Classic Plans ---
    {"q": "What is the annual limit for Classic 2?", "expect_found": True, "tag": "classic"},
    {"q": "Does Classic 1R cover maternity?", "expect_found": True, "tag": "classic"},

    # --- Unsupported Plan Fallback ---
    {"q": "What is the annual limit for Remedy 05?", "expect_found": False, "tag": "unsupported_plan"},
    {"q": "What is the annual limit for Remedy 06?", "expect_found": False, "tag": "unsupported_plan"},
    {"q": "Does Remedy 10 cover dental?", "expect_found": False, "tag": "unsupported_plan"},
    {"q": "What benefits does Prime 1 have?", "expect_found": False, "tag": "excluded_plan"},
    {"q": "What is the annual limit for Classic 1?", "expect_found": False, "tag": "excluded_plan"},

    # --- Arabic that may fail routing ---
    {"q": "ما هي التغطية في ريمدي 02؟", "expect_found": True, "tag": "arabic_routing"},
    {"q": "شو فوائد ريمدي 03؟", "expect_found": True, "tag": "arabic_routing"},

    # --- Mixed Arabic-English ---
    {"q": "هل dental مغطى في Remedy 02?", "expect_found": True, "tag": "mixed_lang"},
    {"q": "Does ريمدي 02 include maternity?", "expect_found": True, "tag": "mixed_lang"},
]


def run_question(q: str) -> str:
    """Run a single question through ask_kb.py and return the output."""
    try:
        r = subprocess.run(
            [sys.executable, str(ASK_KB), q],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        return r.stdout.strip()
    except Exception as e:
        return f"(error: {e})"


def main():
    passed = 0
    failed = 0
    results = []

    for i, item in enumerate(QUESTIONS, 1):
        answer = run_question(item["q"])
        is_no_answer = (not answer or answer == "No answer found.")

        if item["expect_found"]:
            ok = not is_no_answer
        else:
            ok = is_no_answer

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        results.append({"i": i, "tag": item["tag"], "status": status, "q": item["q"], "answer": answer})
        print(f"[{status}] Q{i} ({item['tag']}): {item['q']}")
        print(f"       >> {answer[:150]}")
        print()

    print("=" * 60)
    print(f"Total: {len(QUESTIONS)}  |  PASS: {passed}  |  FAIL: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
