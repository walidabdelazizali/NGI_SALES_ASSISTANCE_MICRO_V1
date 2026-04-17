"""
Regression tests for the Conversational Hotfix Pack (6 issues).
Each test maps to a specific issue and validation query from the hotfix spec.
"""
import subprocess
import sys
import pytest


def run_ask_kb(query):
    result = subprocess.run(
        [sys.executable, "scripts/ask_kb.py", query],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip()


# --- Issue 1: Prenatal plan leakage ---
class TestIssue1PrenatalLeakage:
    def test_r06_prenatal_returns_r06(self):
        out = run_ask_kb("Does Remedy 06 include prenatal services?")
        assert "remedy 06" in out.lower() or "Remedy 06" in out
        assert "remedy 02" not in out.lower()

    def test_r04_prenatal_returns_r04(self):
        out = run_ask_kb("Does Remedy 04 include prenatal services?")
        assert "remedy 04" in out.lower() or "Remedy 04" in out

    def test_r05_newborn_returns_r05(self):
        out = run_ask_kb("Does Remedy 05 include newborn cover?")
        assert "remedy 05" in out.lower() or "Remedy 05" in out


# --- Issue 2: Arabic maternity waiting period ---
class TestIssue2ArabicWP:
    def test_arabic_wp_r05(self):
        out = run_ask_kb("فترة انتظار الحمل في Remedy 05 كام؟")
        out_lower = out.lower()
        assert "waiting period" in out_lower or "nil" in out_lower or "فترة" in out

    def test_arabic_wp_r03(self):
        out = run_ask_kb("مدة انتظار الحمل في Remedy 03؟")
        out_lower = out.lower()
        assert "waiting period" in out_lower or "nil" in out_lower or "month" in out_lower or "فترة" in out


# --- Issue 3: Arabic direct access / referral ---
class TestIssue3ArabicDirectAccess:
    def test_arabic_direct_access_r05(self):
        out = run_ask_kb("هل Remedy 05 فيها دخول مباشر على specialist؟")
        out_lower = out.lower()
        assert "referral" in out_lower or "direct" in out_lower or "specialist" in out_lower or "تحويل" in out

    def test_english_specialist_r04(self):
        out = run_ask_kb("Do I need a GP referral for specialist in Remedy 04?")
        out_lower = out.lower()
        assert "referral" in out_lower or "specialist" in out_lower


# --- Issue 4: Vaccine routing ---
class TestIssue4VaccineRouting:
    def test_r04_influenza(self):
        out = run_ask_kb("Does Remedy 04 cover the influenza vaccine?")
        out_lower = out.lower()
        assert "influenza" in out_lower
        assert "covered" in out_lower or "once per year" in out_lower

    def test_r05_shingrix_not_listed(self):
        out = run_ask_kb("Is the Shingrix vaccine covered under Remedy 05?")
        out_lower = out.lower()
        assert "not listed" in out_lower or "not covered" in out_lower

    def test_r06_shingrix_covered(self):
        out = run_ask_kb("Is the Shingrix vaccine covered under Remedy 06?")
        out_lower = out.lower()
        assert "shingrix" in out_lower
        assert "covered" in out_lower


# --- Issue 5: Network negative verdict ---
class TestIssue5NetworkVerdict:
    def test_cleveland_clinic_not_confirmed(self):
        out = run_ask_kb("Is Cleveland Clinic Abu Dhabi in the network for Remedy 05?")
        out_lower = out.lower()
        assert "not confirmed" in out_lower or "not found" in out_lower or "not in" in out_lower

    def test_nmc_royal_in_network(self):
        out = run_ask_kb("Is NMC Royal Hospital in the network for Remedy 04?")
        out_lower = out.lower()
        assert "nmc royal" in out_lower
        assert "in network" in out_lower


# --- Issue 6: Unlimited qualifier ---
class TestIssue6UnlimitedQualifier:
    def test_unlimited_dental_r04_denial(self):
        out = run_ask_kb("Is dental coverage unlimited under Remedy 04?")
        out_lower = out.lower()
        assert "not unlimited" in out_lower or "no, it is not unlimited" in out_lower

    def test_normal_dental_r04_no_denial(self):
        out = run_ask_kb("Does Remedy 04 include dental?")
        out_lower = out.lower()
        assert "not unlimited" not in out_lower
        assert "dental" in out_lower
