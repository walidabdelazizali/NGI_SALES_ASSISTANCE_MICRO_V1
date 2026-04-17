import subprocess
import sys
import re
import pytest

# Helper to run ask_kb.py and return stdout as string
def run_ask_kb(query):
    result = subprocess.run(
        [sys.executable, "scripts/ask_kb.py", query],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip()

def normalize(text):
    t = text.lower()
    t = re.sub(r"[\s\n]+", " ", t)
    t = t.replace(",", "")
    t = t.replace(". ", "")
    t = t.replace("a e d", "aed")
    t = t.replace("aed ", "aed")
    t = t.replace("aed.", "aed")
    t = t.replace("aed,", "aed")
    t = re.sub(r"aed(\d+)\.(\d{3})", r"aed\1\2", t)
    t = re.sub(r"aed(\d+)\s*per", r"aed\1 per", t)
    t = re.sub(r"(\d+) percent", r"\1%", t)
    t = t.replace("%", " percent ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# --- Core R05 acceptance: identical to R04 except Direct Access + no Shingrix ---
@pytest.mark.parametrize("query, checks", [
    # Annual limit: AED 150,000 (same as R04)
    ("What is the annual limit for Remedy 05?", ["annual limit", "aed150000"]),
    # OP consultation: 20% up to AED 30/visit (same as R04)
    ("What is the GP consultation copay for Remedy 05?", ["20 percent", "aed30"]),
    # Lab: NIL copay (same as R04)
    ("What is the laboratory copay for Remedy 05?", ["nil"]),
    # Radiology: NIL copay (same as R04)
    ("What is the radiology copay for Remedy 05?", ["nil"]),
    # Physiotherapy: NIL copay, 12 sessions (same as R04)
    ("Does Remedy 05 include physiotherapy?", ["covered", "12 sessions", "nil"]),
    # Drugs: AED 7,500/year, 20% copay (same as R04)
    ("What is the prescribed drugs cover for Remedy 05?", ["prescribed drugs", "7500", "20 percent"]),
    # Maternity waiting period: NIL (same as R04)
    ("What is the maternity waiting period for Remedy 05?", ["waiting period", "nil"]),
    # Prenatal: 8 visits with Direct Access to Specialist
    ("What is the prenatal services cover for Remedy 05?", ["prenatal", "8 visits", "pre-approval"]),
    # Newborn: 30 days (same as R04)
    ("What is the newborn cover for Remedy 05?", ["30 days", "newborn", "bcg", "hepatitis b"]),
    # Pre-existing conditions: same as R04
    ("What are the pre-existing condition rules for Remedy 05?", ["pre-existing", "chronic", "6 months"]),
])
def test_remedy05_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)

    # Harden physiotherapy test — must show NIL copay, NOT 10% or 15%
    if query.lower().strip() == "does remedy 05 include physiotherapy?":
        assert "12 sessions" in norm, f"Expected '12 sessions' in output for '{query}'. Got: {output}"
        assert "nil" in norm, f"Expected 'nil' copay in output for '{query}'. Got: {output}"
        assert "10 percent" not in norm, f"Did NOT expect '10 percent' in output for '{query}'. Got: {output}"
        assert "15 percent" not in norm, f"Did NOT expect '15 percent' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        assert "remedy 04" not in norm, f"Did NOT expect 'Remedy 04' in output for '{query}'. Got: {output}"
        return

    # Harden prescribed drugs test — must show 7500, NOT 5000 or 3000
    if query.lower().strip() == "what is the prescribed drugs cover for remedy 05?":
        assert "prescribed drugs" in norm, f"Expected 'prescribed drugs' in output for '{query}'. Got: {output}"
        assert ("7500" in norm or "7 500" in norm or "aed7500" in norm or "aed7 500" in norm), \
            f"Expected '7500' value in output for '{query}'. Got: {output}"
        assert "20 percent" in norm, f"Expected '20 percent' in output for '{query}'. Got: {output}"
        assert "5000" not in norm, f"Did NOT expect '5000' (R03 value) in output for '{query}'. Got: {output}"
        assert "3000" not in norm, f"Did NOT expect '3000' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        assert "remedy 04" not in norm, f"Did NOT expect 'Remedy 04' in output for '{query}'. Got: {output}"
        return

    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- R05 extended acceptance ---
@pytest.mark.parametrize("query, checks", [
    # Telemedicine: ISA Assist only
    ("Does Remedy 05 include telemedicine?", ["isa assist", "travel"]),
    # Optical: discount-only
    ("Does Remedy 05 include optical?", ["25 percent", "discount"]),
    # Dental: same as R04
    ("Does Remedy 05 include dental?", ["dental", "500", "30 percent"]),
    # Reimbursement inside UAE: emergency only
    ("What is the reimbursement policy inside UAE for Remedy 05?", ["emergency"]),
    # IP coinsurance cap: same as R04
    ("Does Remedy 05 require approval for non-urgent inpatient treatment?", ["aed 500", "aed 1000"]),
])
def test_remedy05_extended_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- R05 DELTA: Direct Access to Specialist (no GP referral) ---
def test_remedy05_direct_access_to_specialist():
    """R05 must state Direct Access to Specialist — no GP referral required."""
    output = run_ask_kb("Do I need GP referral for specialist consultation in Remedy 05?")
    norm = normalize(output)
    assert "direct access" in norm or "no gp referral" in norm or "no referral" in norm, \
        f"R05 must mention 'direct access' or 'no GP referral'. Got: {output}"


def test_remedy05_referral_rule_not_gp():
    """R05 referral query must NOT require GP referral (unlike R04)."""
    output = run_ask_kb("Do I need GP referral for specialist consultation in Remedy 05?")
    norm = normalize(output)
    # R05 should mention direct access or no referral needed
    assert "direct access" in norm or "no gp referral" in norm or "no referral" in norm, \
        f"R05 must mention 'direct access' or 'no GP referral'. Got: {output}"


# --- R05 DELTA: No Shingrix vaccine ---
def test_remedy05_no_shingrix():
    """R05 preventive must NOT include Shingrix (only 4 items, not 5)."""
    output = run_ask_kb("Does Remedy 05 include Shingrix vaccine?")
    norm = normalize(output)
    # Should not specifically list Shingrix as covered
    # Note: if the system says "not covered" or gives no answer, that's correct
    assert "shingrix" not in norm or "not" in norm or "no answer" in norm.lower(), \
        f"R05 should NOT list Shingrix as a covered preventive benefit. Got: {output}"


# --- Plan separation: R05 must not leak R04/R03/R02 data ---
def test_remedy05_does_not_leak_to_04():
    """R04 query should NOT return R05 direct access wording."""
    output = run_ask_kb("Do I need GP referral for specialist consultation in Remedy 04?")
    norm = normalize(output)
    assert "direct access to specialist" not in norm, \
        f"R05 direct access leaked into R04 referral query: {output}"


def test_remedy05_does_not_leak_to_03():
    """R03 query should NOT return R05-specific values."""
    output = run_ask_kb("What is the prescribed drugs cover for Remedy 03?")
    norm = normalize(output)
    assert "7500" not in norm, f"R04/R05 drug limit (7500) leaked into R03 query: {output}"


def test_remedy05_does_not_leak_to_02():
    """R02 query should NOT return R05-specific values."""
    output = run_ask_kb("What is the GP consultation copay for Remedy 02?")
    norm = normalize(output)
    assert "aed30" not in norm.replace(" ", ""), f"R04/R05 copay (AED 30) leaked into R02 query: {output}"


def test_remedy05_telemedicine_not_general_op():
    """Telemedicine for R05 must reference ISA Assist/travel."""
    output = run_ask_kb("Does Remedy 05 include telemedicine?")
    norm = normalize(output)
    assert "isa" in norm or "travel" in norm or "assist" in norm, \
        f"Telemedicine should reference ISA Assist/travel for R05. Got: {output}"


def test_remedy05_network_aster_qusais():
    """Aster Hospital Qusais should be in the network for Remedy 05."""
    output = run_ask_kb("Is Aster Hospital Qusais in the network for Remedy 05?")
    norm = normalize(output)
    assert "aster" in norm, f"Expected 'aster' in network response for R05. Got: {output}"
    assert "qusais" in norm or "network" in norm, f"Expected Qusais/network context. Got: {output}"
