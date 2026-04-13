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
    t = re.sub(r"aed(\d+)\.(\d{3})", r"aed\1\2", t)  # aed3.000 -> aed3000
    t = re.sub(r"aed(\d+)\s*per", r"aed\1 per", t)
    t = re.sub(r"(\d+) percent", r"\1%", t)
    t = t.replace("%", " percent ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# --- Core R04 acceptance: deltas from R03 ---
@pytest.mark.parametrize("query, checks", [
    # Annual limit: same as R03 = AED 150,000
    ("What is the annual limit for Remedy 04?", ["annual limit", "aed150000"]),
    # OP consultation: 20% up to AED 30/visit (R03 was 10%)
    ("What is the GP consultation copay for Remedy 04?", ["20 percent", "aed30"]),
    # Lab: NIL copay (R03 was 10%)
    ("What is the laboratory copay for Remedy 04?", ["nil"]),
    # Radiology: NIL copay (R03 was 10%)
    ("What is the radiology copay for Remedy 04?", ["nil"]),
    # Physiotherapy: NIL copay, 12 sessions (R03 was 10%)
    ("Does Remedy 04 include physiotherapy?", ["covered", "12 sessions", "nil"]),
    # Drugs: AED 7,500/year, 20% copay (R03 was AED 5,000)
    ("What is the prescribed drugs cover for Remedy 04?", ["prescribed drugs", "7500", "20 percent"]),
    # Maternity waiting period: NIL (same as R03)
    ("What is the maternity waiting period for Remedy 04?", ["waiting period", "nil"]),
    # Prenatal: same as R03
    ("What is the prenatal services cover for Remedy 04?", ["prenatal", "8 visits", "pre-approval"]),
    # Newborn: same as R03
    ("What is the newborn cover for Remedy 04?", ["30 days", "newborn", "bcg", "hepatitis b"]),
    # Pre-existing conditions: same as R03
    ("What are the pre-existing condition rules for Remedy 04?", ["pre-existing", "chronic", "6 months"]),
])
def test_remedy04_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)

    # Harden physiotherapy test — must show NIL copay, NOT 10% or 15%
    if query.lower().strip() == "does remedy 04 include physiotherapy?":
        assert "12 sessions" in norm, f"Expected '12 sessions' in output for '{query}'. Got: {output}"
        assert "nil" in norm, f"Expected 'nil' copay in output for '{query}'. Got: {output}"
        assert "10 percent" not in norm, f"Did NOT expect '10 percent' in output for '{query}'. Got: {output}"
        assert "15 percent" not in norm, f"Did NOT expect '15 percent' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        return

    # Harden prescribed drugs test — must show 7500, NOT 5000 or 3000
    if query.lower().strip() == "what is the prescribed drugs cover for remedy 04?":
        assert "prescribed drugs" in norm, f"Expected 'prescribed drugs' in output for '{query}'. Got: {output}"
        assert ("7500" in norm or "7 500" in norm or "aed7500" in norm or "aed7 500" in norm), \
            f"Expected '7500' value in output for '{query}'. Got: {output}"
        assert "20 percent" in norm, f"Expected '20 percent' in output for '{query}'. Got: {output}"
        assert "5000" not in norm, f"Did NOT expect '5000' (R03 value) in output for '{query}'. Got: {output}"
        assert "3000" not in norm, f"Did NOT expect '3000' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        return

    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- R04 extended acceptance ---
@pytest.mark.parametrize("query, checks", [
    # Telemedicine: ISA Assist only, NOT general OP
    ("Does Remedy 04 include telemedicine?", ["isa assist", "travel"]),
    # Optical: discount-only, not insured benefit
    ("Does Remedy 04 include optical?", ["25 percent", "discount"]),
    # Dental: same as R03
    ("Does Remedy 04 include dental?", ["dental", "500", "30 percent"]),
    # Reimbursement inside UAE: emergency only
    ("What is the reimbursement policy inside UAE for Remedy 04?", ["emergency"]),
    # IP coinsurance cap: same as R03
    ("Does Remedy 04 require approval for non-urgent inpatient treatment?", ["aed 500", "aed 1000"]),
])
def test_remedy04_extended_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- Plan separation: R04 must not leak R03 or R02 data ---
def test_remedy04_does_not_leak_to_03():
    """Remedy 03 query should NOT return R04-specific values."""
    output = run_ask_kb("What is the prescribed drugs cover for Remedy 03?")
    norm = normalize(output)
    assert "7500" not in norm, f"Remedy 04 drug limit (7500) leaked into Remedy 03 query: {output}"


def test_remedy04_does_not_leak_to_02():
    """Remedy 02 query should NOT return R04-specific values."""
    output = run_ask_kb("What is the GP consultation copay for Remedy 02?")
    norm = normalize(output)
    # R02 copay is 15%, not 20%/AED 30
    assert "aed30" not in norm.replace(" ", ""), f"Remedy 04 copay (AED 30) leaked into Remedy 02 query: {output}"


def test_remedy04_telemedicine_not_general_op():
    """Telemedicine for Remedy 04 must NOT be presented as a general outpatient benefit."""
    output = run_ask_kb("Does Remedy 04 include telemedicine?")
    norm = normalize(output)
    assert "isa" in norm or "travel" in norm or "assist" in norm, \
        f"Telemedicine should reference ISA Assist/travel for Remedy 04. Got: {output}"


def test_remedy04_network_aster_qusais():
    """Aster Hospital Qusais should be in the network for Remedy 04."""
    output = run_ask_kb("Is Aster Hospital Qusais in the network for Remedy 04?")
    norm = normalize(output)
    assert "aster" in norm, f"Expected 'aster' in network response for Remedy 04. Got: {output}"
    assert "qusais" in norm or "network" in norm, f"Expected Qusais/network context. Got: {output}"
