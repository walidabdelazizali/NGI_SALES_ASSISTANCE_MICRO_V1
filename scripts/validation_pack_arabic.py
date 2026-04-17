"""
Arabic Coverage Validation Pack — Phase 3.

Focused on Arabic and mixed Arabic-English queries across
all 10 priority areas: annual limit, area of coverage, maternity,
dental, telemedicine, network, direct billing, copay/coinsurance,
approvals/referral, reimbursement.

Run:
    cd NGI_SALES_ASSISTANCE_MICRO_V1
    python scripts/validation_pack_arabic.py

Output: prints each question, the KB answer, and a PASS/FAIL tag.
"""

import subprocess
import sys
from pathlib import Path

ASK_KB = Path(__file__).resolve().parent / "ask_kb.py"
PROJECT_ROOT = ASK_KB.parent.parent

QUESTIONS = [
    # --- Annual Limit (Arabic) ---
    {"q": "شو الحد السنوي لريمدي 02؟", "expect_found": True, "tag": "annual_limit_ar"},
    {"q": "كم الحد السنوي لريمدي 03؟", "expect_found": True, "tag": "annual_limit_ar"},
    {"q": "الليمت السنوي ريمدي 04", "expect_found": True, "tag": "annual_limit_ar"},

    # --- Area of Coverage (Arabic) ---
    {"q": "وين التغطية في ريمدي 02؟", "expect_found": True, "tag": "area_coverage_ar"},
    {"q": "نطاق التغطية لريمدي 03", "expect_found": True, "tag": "area_coverage_ar"},
    {"q": "منطقة التغطية ريمدي 04", "expect_found": True, "tag": "area_coverage_ar"},

    # --- Maternity (Arabic) ---
    {"q": "هل ريمدي 02 فيها تغطية حمل؟", "expect_found": True, "tag": "maternity_ar"},
    {"q": "تغطية الولادة في ريمدي 03", "expect_found": True, "tag": "maternity_ar"},
    {"q": "حمل وولادة ريمدي 04", "expect_found": True, "tag": "maternity_ar"},

    # --- Dental (Arabic) ---
    {"q": "هل ريمدي 02 فيها أسنان؟", "expect_found": True, "tag": "dental_ar"},
    {"q": "تغطية الاسنان ريمدي 03", "expect_found": True, "tag": "dental_ar"},
    {"q": "هل في أسنان في ريمدي 04؟", "expect_found": True, "tag": "dental_ar"},

    # --- Telemedicine (Arabic) ---
    {"q": "هل تيليمديسن مغطى في ريمدي 02؟", "expect_found": True, "tag": "telemedicine_ar"},
    {"q": "استشارة عن بعد ريمدي 03", "expect_found": True, "tag": "telemedicine_ar"},

    # --- Network (Arabic) ---
    {"q": "هل أستر القصيص ضمن شبكة ريمدي 02؟", "expect_found": True, "tag": "network_ar"},
    {"q": "مستشفيات الشبكة ريمدي 03", "expect_found": True, "tag": "network_ar"},
    {"q": "ضمن الشبكة ريمدي 02", "expect_found": True, "tag": "network_ar"},

    # --- Direct Billing (Arabic) ---
    {"q": "ديركت بيلنج ريمدي 02", "expect_found": True, "tag": "direct_billing_ar"},

    # --- Copay / Coinsurance (Arabic) ---
    {"q": "كم الكوبي في ريمدي 02؟", "expect_found": True, "tag": "copay_ar"},
    {"q": "نسبة التحمل ريمدي 03", "expect_found": True, "tag": "copay_ar"},

    # --- Approvals / Referral (Arabic) ---
    {"q": "هل لازم تحويل من طبيب عام في ريمدي 02؟", "expect_found": True, "tag": "referral_ar"},
    {"q": "محتاج موافقة مسبقة ريمدي 03؟", "expect_found": True, "tag": "approval_ar"},
    {"q": "بري ابروفال ريمدي 04", "expect_found": True, "tag": "approval_ar"},

    # --- Reimbursement (Arabic) ---
    {"q": "استرداد ريمدي 02", "expect_found": True, "tag": "reimbursement_ar"},
    {"q": "تعويض ريمدي 03", "expect_found": True, "tag": "reimbursement_ar"},

    # --- Generic Arabic (coverage / benefits) ---
    {"q": "ما هي التغطية في ريمدي 02؟", "expect_found": True, "tag": "generic_ar"},
    {"q": "شو فوائد ريمدي 03؟", "expect_found": True, "tag": "generic_ar"},
    {"q": "المزايا في ريمدي 04", "expect_found": True, "tag": "generic_ar"},

    # --- Mixed Arabic-English ---
    {"q": "هل dental مغطى في Remedy 02?", "expect_found": True, "tag": "mixed_lang"},
    {"q": "Does ريمدي 02 include maternity?", "expect_found": True, "tag": "mixed_lang"},
    {"q": "annual limit ريمدي 03", "expect_found": True, "tag": "mixed_lang"},
]


def run_question(q: str) -> str:
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
    print(f"Arabic Validation Pack: {passed} PASS / {failed} FAIL out of {len(QUESTIONS)}")
    if failed:
        print("\nFailed questions:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  Q{r['i']} ({r['tag']}): {r['q']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
