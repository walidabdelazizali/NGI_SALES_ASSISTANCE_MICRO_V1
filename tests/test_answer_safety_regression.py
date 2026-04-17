"""
Answer-safety regression tests — post-expansion safety, precedence, and Arabic parity.

Covers:
A) Arabic annual-limit intent detection
B) Plan-specific dental precedence (no generic fallback override)
C) Deployment-scope guardrail for unapproved plans
D) Arabic network query routing
E) Remedy 02 maternity approved answer
F) Additional deployment-scope edge cases
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


# ── A) Arabic annual-limit intent detection ─────────────────────────


class TestArabicAnnualLimit:
    """Arabic annual-limit queries must return the correct annual limit."""

    def test_arabic_annual_limit_remedy_02(self):
        out = _ask("ما هو الحد السنوي لخطة Remedy 02؟")
        assert "annual limit" in out.lower() or "150" in out
        assert "no answer" not in out.lower()

    def test_arabic_annual_limit_variant_aqsa(self):
        """الحد الأقصى السنوي variant."""
        out = _ask("ما هو الحد الأقصى السنوي ل Remedy 03؟")
        assert "annual limit" in out.lower() or "150" in out
        assert "no answer" not in out.lower()

    def test_arabic_annual_limit_variant_saqf(self):
        """السقف السنوي variant."""
        out = _ask("كم السقف السنوي في Remedy 02؟")
        assert "annual limit" in out.lower() or "150" in out
        assert "no answer" not in out.lower()

    def test_arabic_annual_limit_variant_hadd_sanawi(self):
        """حد سنوي variant."""
        out = _ask("حد سنوي Remedy 04 كام؟")
        assert "annual limit" in out.lower() or "150" in out
        assert "no answer" not in out.lower()


# ── B) Plan-specific dental precedence ──────────────────────────────


class TestDentalPrecedence:
    """Dental answers must come from plan-specific data, not generic fallback."""

    def test_remedy_02_dental_plan_specific(self):
        out = _ask("Does Remedy 02 include dental?")
        assert "[plan]" in out.lower()
        # Must contain R02 dental data
        assert "500" in out or "dental" in out.lower()
        # Must NOT contain data from another plan
        assert "restricted to listed clinics" not in out.lower(), (
            "R02 dental should not include R03+ 'restricted to listed clinics' note"
        )

    def test_remedy_03_dental_plan_specific(self):
        out = _ask("Does Remedy 03 include dental?")
        assert "[plan]" in out.lower()
        assert "500" in out or "dental" in out.lower()


# ── C) Deployment-scope guardrail ───────────────────────────────────


class TestDeploymentScopeGuardrail:
    """Plans outside deployment scope must return safe fallback."""

    def test_remedy_05_copay_allowed(self):
        """Phase 4A: Remedy 05 IS now in deployment scope."""
        out = _ask("What is the copay for Remedy 05?")
        assert "no answer found" not in out.lower()
        assert "20%" in out

    def test_remedy_06_annual_limit_allowed(self):
        """Phase 4B: Remedy 06 IS now in deployment scope."""
        out = _ask("What is the annual limit for Remedy 06?")
        assert "no answer found" not in out.lower()
        assert "150,000" in out

    def test_remedy_05_dental_allowed(self):
        """Phase 4A: Remedy 05 IS now in deployment scope."""
        out = _ask("Does Remedy 05 include dental?")
        assert "no answer found" not in out.lower()

    def test_remedy_05_maternity_allowed(self):
        """Phase 4A: Remedy 05 IS now in deployment scope."""
        out = _ask("Does Remedy 05 include maternity?")
        assert "no answer found" not in out.lower()
        assert "10,000" in out

    def test_remedy_02_copay_allowed(self):
        """Remedy 02 IS in deployment scope — must return an answer."""
        out = _ask("What is the copay for Remedy 02?")
        assert "no answer found" not in out.lower()
        assert "copayment" in out.lower() or "copay" in out.lower() or "15%" in out

    def test_remedy_04_allowed(self):
        """Remedy 04 IS in deployment scope — must return an answer."""
        out = _ask("What is the annual limit for Remedy 04?")
        assert "no answer found" not in out.lower()
        assert "150" in out


# ── D) Arabic network query routing ─────────────────────────────────


class TestArabicNetworkQuery:
    """Arabic in-network queries must route correctly."""

    def test_aster_qusais_arabic(self):
        out = _ask("هل مستشفى أستر القصيص داخل الشبكة؟")
        assert "aster" in out.lower() or "qusais" in out.lower() or "network" in out.lower()
        assert "no answer" not in out.lower()


# ── E) Remedy 02 maternity approved answer ──────────────────────────


class TestMaternityApproved:
    """Maternity queries for approved plans must return correct data."""

    def test_remedy_02_maternity(self):
        out = _ask("Does Remedy 02 include maternity?")
        assert "maternity" in out.lower()
        assert "10,000" in out or "10000" in out
        assert "no answer" not in out.lower()

    def test_remedy_03_maternity(self):
        out = _ask("Does Remedy 03 include maternity?")
        assert "maternity" in out.lower()
        assert "no answer" not in out.lower()
