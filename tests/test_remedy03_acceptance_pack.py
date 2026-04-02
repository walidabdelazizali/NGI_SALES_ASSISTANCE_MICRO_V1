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

@pytest.mark.parametrize("query, checks", [
    ("What is the annual limit for Remedy 03?", ["annual limit", "aed150000"]),
    ("What is the provider network for Remedy 03?", ["hn basic plus"]),
    ("What is the area of coverage for Remedy 03?", ["uae", "indian sub-continent", "south east asia", "hong kong", "singapore"]),
    ("Does Remedy 03 include physiotherapy?", ["covered", "12 sessions", "10 percent", "pre-approval"]),
    ("What is the prescribed drugs cover for Remedy 03?", ["prescribed drugs", "5000", "20 percent", "pre-approval", "excess over annual limit not covered"]),
    ("What are the pre-existing condition rules for Remedy 03?", ["pre-existing", "chronic", "6 months", "undeclared", "not covered"]),
    ("Do I need GP referral for specialist consultation in Remedy 03?", ["gp referral", "specialist consultation", "remedy 03"]),
    ("Does Remedy 03 require approval for non-urgent inpatient treatment?", ["pre-approval required", "20 percent", "aed 500", "aed 1000", "remedy 03"]),
    ("What is the maternity waiting period for Remedy 03?", ["waiting period", "nil"]),
    ("What is the prenatal services cover for Remedy 03?", ["prenatal", "8 visits", "10 percent", "pre-approval"]),
    ("What is the newborn cover for Remedy 03?", ["30 days", "newborn", "bcg", "hepatitis b", "neonatal screening"]),
])
def test_remedy03_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)

    # Harden physiotherapy test
    if query.lower().strip() == "does remedy 03 include physiotherapy?":
        assert "12 sessions" in norm, f"Expected '12 sessions' in output for '{query}'. Got: {output}"
        assert "10 percent" in norm, f"Expected '10 percent' in output for '{query}'. Got: {output}"
        assert "pre-approval" in norm, f"Expected 'pre-approval' in output for '{query}'. Got: {output}"
        assert "15 percent" not in norm, f"Did NOT expect '15 percent' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        return

    # Harden prescribed drugs test
    if query.lower().strip() == "what is the prescribed drugs cover for remedy 03?":
        assert "prescribed drugs" in norm, f"Expected 'prescribed drugs' in output for '{query}'. Got: {output}"
        assert ("5000" in norm or "5 000" in norm or "aed5000" in norm or "aed5 000" in norm), f"Expected '5000' value in output for '{query}'. Got: {output}"
        assert "20 percent" in norm, f"Expected '20 percent' in output for '{query}'. Got: {output}"
        assert "pre-approval" in norm, f"Expected 'pre-approval' in output for '{query}'. Got: {output}"
        assert "excess over annual limit not covered" in norm, f"Expected 'excess over annual limit not covered' in output for '{query}'. Got: {output}"
        assert "3000" not in norm, f"Did NOT expect '3000' in output for '{query}'. Got: {output}"
        assert "30 percent" not in norm, f"Did NOT expect '30 percent' in output for '{query}'. Got: {output}"
        assert "remedy 02" not in norm, f"Did NOT expect 'Remedy 02' in output for '{query}'. Got: {output}"
        return

    # Slightly strengthen other checks for business specificity
    for check in checks:
        assert check.replace(" ","") in norm.replace(" ",""), f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- Plan separation and unsupported plan negative tests ---
def test_remedy03_does_not_leak_to_02():
    output = run_ask_kb("What is the annual limit for Remedy 02?")
    norm = normalize(output)
    assert "150000" not in norm or "remedy 03" not in norm, f"Remedy 03 data leaked for Remedy 02 query: {output}"

def test_remedy03_unsupported_plan():
    output = run_ask_kb("What is the annual limit for Remedy 04?")
    norm = normalize(output)
    assert "not supported" in norm or "no answer found" in norm, f"Unsupported plan did not return correct negative: {output}"
