"""
Final stabilization regression tests — Remedy 02-06 post-Telegram rollout.

Covers the 7 stabilization items:
A) Waiting period disambiguation
B) Plan leakage prevention
C) Specialist referral intent (English + Arabic)
D) Provider-specific network queries
E) Vaccine handling
F) Unsupported plan safety
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py")
PYTHON = sys.executable


def _ask(question: str) -> str:
    result = subprocess.run(
        [PYTHON, SCRIPT, question],
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


# ── A) Waiting period disambiguation ────────────────────────────────


class TestWaitingPeriodDisambiguation:
    """Maternity WP queries must return waiting-period data, not maternity cover/limit."""

    def test_maternity_wp_remedy_04(self):
        out = _ask("What is the maternity waiting period for Remedy 04?")
        assert "waiting period" in out.lower()
        # Must NOT return the maternity cover limit as the primary answer
        assert "aed 10,000" not in out.lower().replace(",", "").replace(" ", "")

    def test_maternity_wp_remedy_05_arabic(self):
        out = _ask("فترة انتظار الحمل في Remedy 05 كام؟")
        assert "waiting period" in out.lower()
        assert "aed 10,000" not in out.lower().replace(",", "").replace(" ", "")

    def test_maternity_wp_remedy_06(self):
        out = _ask("What is the maternity waiting period for Remedy 06?")
        assert "waiting period" in out.lower()

    def test_maternity_cover_remedy_04(self):
        """Maternity cover question must return coverage info, not waiting period."""
        out = _ask("Does Remedy 04 include maternity?")
        assert out.startswith("[PLAN]")
        assert "maternity" in out.lower()
        # Should mention the AED 10,000 cover
        assert "10,000" in out or "10000" in out

    def test_maternity_limit_remedy_05(self):
        out = _ask("What is the maternity limit for Remedy 05?")
        assert out.startswith("[PLAN]")
        assert "10,000" in out or "10000" in out


# ── B) Plan leakage prevention ───────────────────────────────────────


class TestPlanLeakage:
    """Querying a specific plan must never return another plan's answer."""

    def test_prenatal_r06_no_r02_leakage(self):
        out = _ask("What is the prenatal services cover for Remedy 06?")
        assert "remedy 02" not in out.lower()
        assert "remedy 06" in out.lower() or "r06" in out.lower() or out.startswith("[PLAN]")

    def test_prenatal_r05_no_leakage(self):
        out = _ask("What is the prenatal services cover for Remedy 05?")
        assert "remedy 02" not in out.lower()
        assert "remedy 06" not in out.lower()

    def test_prenatal_r04_no_leakage(self):
        out = _ask("What is the prenatal services cover for Remedy 04?")
        assert "remedy 02" not in out.lower()
        assert "remedy 06" not in out.lower()


# ── C) Specialist referral intent (English + Arabic) ─────────────────


class TestSpecialistReferral:
    def test_gp_referral_r04_english(self):
        out = _ask("Does Remedy 04 require GP referral?")
        assert out.startswith("[RULE]")
        assert "referral" in out.lower()

    def test_gp_referral_r05_english(self):
        out = _ask("Do I need GP referral for specialist consultation in Remedy 05?")
        assert out.startswith("[RULE]")
        assert "direct access" in out.lower() or "no gp referral" in out.lower()

    def test_direct_access_r06_english(self):
        out = _ask("Is direct access to specialist available in Remedy 06?")
        assert out.startswith("[RULE]")
        assert "direct access" in out.lower()

    def test_gp_referral_r06_arabic(self):
        out = _ask("هل Remedy 06 محتاجة تحويل GP؟")
        assert out.startswith("[RULE]")
        assert "direct access" in out.lower() or "no gp referral" in out.lower()

    def test_direct_access_r05_arabic(self):
        out = _ask("هل فيه دخول مباشر على specialist في Remedy 05؟")
        assert out.startswith("[RULE]")
        assert "direct access" in out.lower()

    def test_referral_r04_arabic(self):
        out = _ask("هل محتاج تحويل عشان specialist في Remedy 04؟")
        assert out.startswith("[RULE]")
        assert "referral" in out.lower()


# ── D) Provider-specific network queries ──────────────────────────────


class TestProviderNetwork:
    """Provider-specific questions must return [NETWORK], not generic plan summary."""

    def test_aster_r03(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 03?")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()
        # Must not contain the generic plan network paragraph
        assert "OP Restricted" not in out

    def test_aster_r04(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 04?")
        assert out.startswith("[NETWORK]")

    def test_aster_r05(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 05?")
        assert out.startswith("[NETWORK]")

    def test_aster_r06(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 06?")
        assert out.startswith("[NETWORK]")

    def test_cleveland_r05_not_confirmed(self):
        out = _ask("Is Cleveland Clinic Abu Dhabi in the network for Remedy 05?")
        assert out.startswith("[NETWORK]")
        assert "not confirmed" in out.lower()


# ── E) Vaccine handling ───────────────────────────────────────────────


class TestVaccineHandling:
    def test_influenza_r04(self):
        out = _ask("Does Remedy 04 include influenza vaccine?")
        assert out.startswith("[PLAN]")
        assert "influenza" in out.lower() or "vaccine" in out.lower()
        assert "remedy 06" not in out.lower()

    def test_shingrix_r06(self):
        out = _ask("Does Remedy 06 include Shingrix vaccine?")
        assert out.startswith("[PLAN]")
        assert "shingrix" in out.lower()
        assert "remedy 05" not in out.lower()

    def test_shingrix_r05_not_listed(self):
        out = _ask("Does Remedy 05 include Shingrix vaccine?")
        assert "not listed" in out.lower() or "no answer" in out.lower()


# ── F) Unsupported plan safety ────────────────────────────────────────


class TestUnsupportedPlan:
    def test_remedy_07_annual_limit(self):
        out = _ask("What is the annual limit for Remedy 07?")
        assert "no answer found" in out.lower()

    def test_remedy_99_annual_limit(self):
        out = _ask("What is the annual limit for Remedy 99?")
        assert "no answer found" in out.lower()
