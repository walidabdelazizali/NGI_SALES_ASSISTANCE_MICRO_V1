"""
Acceptance tests for provider/network/direct-billing routing.

Ensures provider-specific questions (known or unknown providers) return
[NETWORK] answers instead of generic plan network descriptions.
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


# ── AT1-AT3: Known provider, different plans ──────────────────────────


class TestKnownProviderInNetwork:
    def test_aster_qusais_remedy_04(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 04?")
        assert out.startswith("[NETWORK]"), f"Expected [NETWORK] tag, got: {out}"
        assert "aster hospital qusais" in out.lower()
        # Must NOT contain the generic plan network paragraph
        assert "OP Restricted" not in out

    def test_aster_qusais_remedy_05(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 05?")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()
        assert "OP Restricted" not in out

    def test_aster_qusais_remedy_06(self):
        out = _ask("Is Aster Hospital Qusais in the network for Remedy 06?")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()


# ── AT4: Direct billing ──────────────────────────────────────────────


class TestDirectBilling:
    def test_aster_direct_billing_remedy_06(self):
        out = _ask("Does Aster Hospital Qusais offer direct billing for Remedy 06?")
        assert out.startswith("[NETWORK]")
        assert "direct billing" in out.lower()
        assert "available" in out.lower()

    def test_nmc_no_direct_billing(self):
        out = _ask("Does NMC Royal Hospital offer direct billing for Remedy 04?")
        assert out.startswith("[NETWORK]")
        assert "not available" in out.lower() or "NOT available" in out

    def test_arabic_direct_billing(self):
        out = _ask("هل Aster Hospital Qusais عندها ديركت بيلنج في Remedy 06؟")
        assert out.startswith("[NETWORK]")
        assert "direct billing" in out.lower()


# ── AT5: Unknown provider → safe not-confirmed ──────────────────────


class TestUnknownProvider:
    def test_cleveland_remedy_05(self):
        out = _ask("Is Cleveland Clinic Abu Dhabi in the network for Remedy 05?")
        assert out.startswith("[NETWORK]")
        assert "not confirmed" in out.lower()

    def test_unknown_provider_arabic(self):
        out = _ask("هل Cleveland Clinic Abu Dhabi ضمن شبكة Remedy 05؟")
        assert out.startswith("[NETWORK]")
        assert "not confirmed" in out.lower()


# ── AT6-AT7: Arabic phrasing for known/unknown providers ─────────────


class TestArabicPhrasing:
    def test_arabic_aster_in_network(self):
        out = _ask("هل Aster Hospital Qusais ضمن شبكة Remedy 06؟")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()

    def test_arabic_inside_network(self):
        out = _ask("هل Aster Hospital Qusais داخل الشبكة لـ Remedy 06؟")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()


# ── Edge cases: alternate phrasing ───────────────────────────────────


class TestAlternatePhrasing:
    def test_part_of_network(self):
        out = _ask("Is Aster Hospital Qusais part of the network for Remedy 04?")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()
        assert "OP Restricted" not in out

    def test_covered_under_partial_name(self):
        """Partial provider name (2-word prefix) should still route to NETWORK."""
        out = _ask("Is Aster Hospital covered under the network for Remedy 05?")
        assert out.startswith("[NETWORK]")

    def test_alias_match(self):
        out = _ask("Is Aster Qs in the network for Remedy 04?")
        assert out.startswith("[NETWORK]")
        assert "aster hospital qusais" in out.lower()


# ── Generic network question must still return plan description ──────


class TestGenericNetworkDescription:
    def test_generic_network_remedy_05(self):
        out = _ask("What is the provider network for Remedy 05?")
        assert out.startswith("[PLAN]")
        assert "HN Basic Plus" in out


# ── Regression: non-network behaviors unchanged ─────────────────────


class TestRegressions:
    def test_annual_limit_remedy_06(self):
        out = _ask("What is the annual limit for Remedy 06?")
        assert out.startswith("[PLAN]")
        assert "150,000" in out

    def test_maternity_wp_remedy_05(self):
        out = _ask("What is the maternity waiting period for Remedy 05?")
        assert out.startswith("[PLAN]")
        assert "nil" in out.lower()

    def test_arabic_referral_remedy_06(self):
        out = _ask("هل Remedy 06 محتاجة تحويل GP؟")
        assert out.startswith("[RULE]")
        assert "direct access" in out.lower() or "no gp referral" in out.lower()

    def test_influenza_remedy_04(self):
        out = _ask("Does Remedy 04 include influenza vaccine?")
        assert out.startswith("[PLAN]")
        assert "influenza" in out.lower() or "vaccine" in out.lower()

    def test_robot_surgery_no_answer(self):
        out = _ask("Does Remedy 06 include robot surgery?")
        assert "no answer found" in out.lower()
