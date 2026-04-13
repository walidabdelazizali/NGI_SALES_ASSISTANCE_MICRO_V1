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


# --- Core R06 acceptance: same as R05 except physio=20 sessions, drugs=AED 10,000, Shingrix added ---
@pytest.mark.parametrize("query, checks", [
    # Annual limit: AED 150,000 (same as R05)
    ("What is the annual limit for Remedy 06?", ["annual limit", "aed150000"]),
    # OP consultation: 20% up to AED 30/visit (same as R05)
    ("What is the GP consultation copay for Remedy 06?", ["20 percent", "aed30"]),
    # Lab: NIL copay (same as R05)
    ("What is the laboratory copay for Remedy 06?", ["nil"]),
    # Radiology: NIL copay (same as R05)
    ("What is the radiology copay for Remedy 06?", ["nil"]),
    # Physiotherapy: NIL copay, 20 sessions (R06 DELTA: was 12 in R05)
    ("Does Remedy 06 include physiotherapy?", ["covered", "20 sessions", "nil"]),
    # Drugs: AED 10,000/year, 20% copay (R06 DELTA: was 7,500 in R05)
    ("What is the prescribed drugs cover for Remedy 06?", ["prescribed drugs", "10000", "20 percent"]),
    # Maternity waiting period: NIL (same as R05)
    ("What is the maternity waiting period for Remedy 06?", ["waiting period", "nil"]),
    # Prenatal: 8 visits with Direct Access to Specialist (same as R05)
    ("What is the prenatal services cover for Remedy 06?", ["prenatal", "8 visits", "pre-approval"]),
    # Newborn: 30 days (same as R05)
    ("What is the newborn cover for Remedy 06?", ["30 days", "newborn", "bcg", "hepatitis b"]),
    # Pre-existing conditions: same as R05
    ("What are the pre-existing condition rules for Remedy 06?", ["pre-existing", "chronic", "6 months"]),
])
def test_remedy06_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)

    # Harden physiotherapy test — must show NIL copay and 20 sessions, NOT 12 (R05) or 10/15%
    if query.lower().strip() == "does remedy 06 include physiotherapy?":
        assert "20 sessions" in norm, f"Expected '20 sessions' in output for '{query}'. Got: {output}"
        assert "nil" in norm, f"Expected 'nil' copay in output for '{query}'. Got: {output}"
        assert "12 sessions" not in norm, f"Did NOT expect '12 sessions' (R05 value) in output for '{query}'. Got: {output}"
        assert "10 percent" not in norm, f"Did NOT expect '10 percent' in output for '{query}'. Got: {output}"
        assert "15 percent" not in norm, f"Did NOT expect '15 percent' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        assert "remedy 05" not in norm, f"Did NOT expect 'Remedy 05' in output for '{query}'. Got: {output}"
        return

    # Harden prescribed drugs test — must show 10000, NOT 7500 (R05) or 5000 (R03) or 3000
    if query.lower().strip() == "what is the prescribed drugs cover for remedy 06?":
        assert "prescribed drugs" in norm, f"Expected 'prescribed drugs' in output for '{query}'. Got: {output}"
        assert ("10000" in norm or "10 000" in norm or "aed10000" in norm or "aed10 000" in norm), \
            f"Expected '10000' value in output for '{query}'. Got: {output}"
        assert "20 percent" in norm, f"Expected '20 percent' in output for '{query}'. Got: {output}"
        assert "7500" not in norm, f"Did NOT expect '7500' (R05 value) in output for '{query}'. Got: {output}"
        assert "5000" not in norm, f"Did NOT expect '5000' (R03 value) in output for '{query}'. Got: {output}"
        assert "3000" not in norm, f"Did NOT expect '3000' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        assert "remedy 03" not in norm, f"Did NOT expect 'Remedy 03' in output for '{query}'. Got: {output}"
        assert "remedy 05" not in norm, f"Did NOT expect 'Remedy 05' in output for '{query}'. Got: {output}"
        return

    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- R06 extended acceptance ---
@pytest.mark.parametrize("query, checks", [
    # Telemedicine: ISA Assist only (same as R05)
    ("Does Remedy 06 include telemedicine?", ["isa assist", "travel"]),
    # Optical: discount-only (same as R05)
    ("Does Remedy 06 include optical?", ["25 percent", "discount"]),
    # Dental: same as R05
    ("Does Remedy 06 include dental?", ["dental", "500", "30 percent"]),
    # Reimbursement inside UAE: emergency only (same as R05)
    ("What is the reimbursement policy inside UAE for Remedy 06?", ["emergency"]),
    # IP coinsurance cap: same as R05
    ("Does Remedy 06 require approval for non-urgent inpatient treatment?", ["aed 500", "aed 1000"]),
])
def test_remedy06_extended_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- R06 DELTA: Direct Access to Specialist (same as R05, no GP referral) ---
def test_remedy06_direct_access_to_specialist():
    """R06 must state Direct Access to Specialist — no GP referral required."""
    output = run_ask_kb("Do I need GP referral for specialist consultation in Remedy 06?")
    norm = normalize(output)
    assert "direct access" in norm or "no gp referral" in norm or "no referral" in norm, \
        f"R06 must mention 'direct access' or 'no GP referral'. Got: {output}"


def test_remedy06_referral_rule_not_gp():
    """R06 referral query must NOT require GP referral (same as R05)."""
    output = run_ask_kb("Do I need GP referral for specialist consultation in Remedy 06?")
    norm = normalize(output)
    assert "direct access" in norm or "no gp referral" in norm or "no referral" in norm, \
        f"R06 must mention 'direct access' or 'no GP referral'. Got: {output}"


# --- R06 DELTA: Shingrix vaccine IS covered (unlike R05 which does NOT have it) ---
def test_remedy06_shingrix_covered():
    """R06 preventive MUST include Shingrix vaccine (5 items, not 4 like R05)."""
    output = run_ask_kb("Does Remedy 06 include Shingrix vaccine?")
    norm = normalize(output)
    assert "shingrix" in norm or "covered" in norm, \
        f"R06 must list Shingrix as a covered preventive benefit. Got: {output}"
    assert "not covered" not in norm and "not supported" not in norm, \
        f"R06 Shingrix should be covered, not rejected. Got: {output}"


def test_remedy06_shingrix_dha_eligibility():
    """R06 Shingrix must mention DHA eligibility criteria."""
    output = run_ask_kb("What are the conditions for Shingrix vaccine under Remedy 06?")
    norm = normalize(output)
    assert "dha" in norm or "eligibility" in norm or "non-lsb" in norm or "dubai visa" in norm, \
        f"R06 Shingrix should mention DHA eligibility. Got: {output}"


# --- R06 DELTA: Physiotherapy 20 sessions (not 12 like R05) ---
def test_remedy06_physio_20_sessions():
    """R06 physiotherapy must state 20 sessions, not 12."""
    output = run_ask_kb("How many physiotherapy sessions are covered for Remedy 06?")
    norm = normalize(output)
    assert "20" in norm, f"Expected '20 sessions' for R06 physio. Got: {output}"
    assert "12" not in norm, f"Did NOT expect '12' (R05 value) for R06 physio. Got: {output}"


# --- R06 DELTA: Prescribed drugs AED 10,000 (not 7,500 like R05) ---
def test_remedy06_drugs_10000():
    """R06 prescribed drugs must state AED 10,000, not 7,500."""
    output = run_ask_kb("What is the annual prescribed drugs limit for Remedy 06?")
    norm = normalize(output)
    assert ("10000" in norm or "10 000" in norm or "aed10000" in norm), \
        f"Expected AED 10,000 for R06 drugs. Got: {output}"
    assert "7500" not in norm, f"Did NOT expect '7500' (R05 value) for R06 drugs. Got: {output}"


# --- Plan separation: R06 must not leak into R05/R04/R03/R02 ---
def test_remedy06_does_not_leak_to_05_physio():
    """R05 physio query should still return 12 sessions, NOT 20 (R06 value)."""
    output = run_ask_kb("Does Remedy 05 include physiotherapy?")
    norm = normalize(output)
    assert "12 sessions" in norm, f"R05 physio should still be 12 sessions. Got: {output}"
    assert "20 sessions" not in norm, f"R06 physio (20 sessions) leaked into R05 query: {output}"


def test_remedy06_does_not_leak_to_05_drugs():
    """R05 drugs query should still return AED 7,500, NOT 10,000 (R06 value)."""
    output = run_ask_kb("What is the prescribed drugs cover for Remedy 05?")
    norm = normalize(output)
    assert ("7500" in norm or "7 500" in norm), f"R05 drugs should still be 7500. Got: {output}"
    assert "10000" not in norm, f"R06 drugs (10000) leaked into R05 query: {output}"


def test_remedy06_does_not_leak_to_04():
    """R04 query should NOT return R06-specific values."""
    output = run_ask_kb("Does Remedy 04 include physiotherapy?")
    norm = normalize(output)
    assert "20 sessions" not in norm, f"R06 physio (20 sessions) leaked into R04 query: {output}"


def test_remedy06_does_not_leak_to_03():
    """R03 query should NOT return R06-specific values."""
    output = run_ask_kb("What is the prescribed drugs cover for Remedy 03?")
    norm = normalize(output)
    assert "10000" not in norm, f"R06 drug limit (10000) leaked into R03 query: {output}"


def test_remedy06_does_not_leak_to_02():
    """R02 query should NOT return R06-specific values."""
    output = run_ask_kb("What is the GP consultation copay for Remedy 02?")
    norm = normalize(output)
    assert "aed30" not in norm.replace(" ", ""), f"R04/R05/R06 copay (AED 30) leaked into R02 query: {output}"


def test_remedy06_telemedicine_not_general_op():
    """Telemedicine for R06 must reference ISA Assist/travel."""
    output = run_ask_kb("Does Remedy 06 include telemedicine?")
    norm = normalize(output)
    assert "isa" in norm or "travel" in norm or "assist" in norm, \
        f"Telemedicine should reference ISA Assist/travel for R06. Got: {output}"


def test_remedy06_network_aster_qusais():
    """Aster Hospital Qusais should be in the network for Remedy 06."""
    output = run_ask_kb("Is Aster Hospital Qusais in the network for Remedy 06?")
    norm = normalize(output)
    assert "aster" in norm, f"Expected 'aster' in network response for R06. Got: {output}"
    assert "qusais" in norm or "network" in norm, f"Expected Qusais/network context. Got: {output}"
