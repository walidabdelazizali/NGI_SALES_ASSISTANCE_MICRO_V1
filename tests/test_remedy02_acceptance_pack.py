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
    # Lowercase, remove extra whitespace, normalize punctuation for semantic checks
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
    # GP/specialist referral normalization
    t = t.replace("gp referral for specialist care", "gp referral specialist referral")
    t = t.replace("specialist network access", "specialist referral")
    return t.strip()

@pytest.mark.parametrize("query, checks", [
    ("What is the annual limit for Remedy 02?", ["annual limit", "aed150000"]),
    ("What is the provider network for Remedy 02?", ["hn basic plus"]),
    ("What is the area of coverage for Remedy 02?", ["uae", "indian sub-continent", "south east asia", "hong kong", "singapore"]),
    ("Does Remedy 02 include physiotherapy?", ["covered", "12 sessions", "15 percent"]),
    ("Does Remedy 02 include MRI?", ["mri", "15 percent", "pre-approval"]),
    ("Does Remedy 02 include CT scan?", ["ct scan", "15 percent", "pre-approval"]),
    ("Does Remedy 02 include laboratory tests?", ["laboratory", "15 percent"]),
    ("Does Remedy 02 include prescribed drugs?", ["prescribed drugs", "3000", "30 percent", "pre-approval"]),
    ("Do I need GP referral for specialist consultation in Remedy 02?", ["gp referral", "specialist referral"]),
    ("What are the pre-existing condition rules for Remedy 02?", ["pre-existing", "chronic", "6 months", "undeclared", "not covered"]),
    ("Does Remedy 02 require approval for non-urgent inpatient treatment?", ["pre-approval required", "20 percent", "aed 500", "aed 1000"]),
    ("What is the maternity waiting period for Remedy 02?", ["waiting period", "nil"]),
    ("What is the maternity limit for Remedy 02?", ["aed 10000"]),
    ("Does Remedy 02 include prenatal services?", ["prenatal", "8 visits", "10 percent", "pre-approval"]),
    ("Does Remedy 02 include newborn cover?", ["30 days", "newborn"]),
])
def test_remedy02_acceptance(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ","") in norm.replace(" ",""), f"Expected '{check}' in output for '{query}'. Got: {output}"

@pytest.mark.parametrize("query, checks", [
    ("Is Aster Hospital Qusais in the network?", ["in network", "hn basic plus", "dubai"]),
    ("Is Burjeel Specialty Hospital Sharjah in the network?", ["in network", "hn basic plus", "sharjah"]),
])
def test_remedy02_network_sanity(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ","") in norm.replace(" ",""), f"Expected '{check}' in output for '{query}'. Got: {output}"


# --- Plan separation and unsupported plan negative tests ---
def test_remedy02_does_not_leak_to_03():
    output = run_ask_kb("What is the annual limit for Remedy 03?")
    norm = normalize(output)
    assert "150000" not in norm or "remedy 02" not in norm, f"Remedy 02 data leaked for Remedy 03 query: {output}"

def test_remedy02_unsupported_plan():
    output = run_ask_kb("What is the annual limit for Remedy 04?")
    norm = normalize(output)
    assert "not supported" in norm or "no answer found" in norm, f"Unsupported plan did not return correct negative: {output}"
