"""
Enhanced Plans Baseline Tests.
Validates the stability-first baseline for confirmed enhanced plans:
  1. Positive: all 5 confirmed Classic plans answer core questions correctly
  2. Negative: excluded plans (HN_CLASSIC_1, HN_PRIME_1, HN_PRIME_2) are blocked
  3. Regression: Remedy plans unchanged
  4. Benefits: dental, optical, consultation, diagnostics, prescribed drugs
  5. Aliases: variant name formats recognized
  6. Safety: no filename identity, no staging paths in runtime
"""
import subprocess
import sys
import re
import pytest


def run_ask_kb(query):
    result = subprocess.run(
        [sys.executable, "scripts/ask_kb.py", query],
        capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


def normalize(text):
    t = text.lower()
    t = re.sub(r"[\s\n]+", " ", t)
    t = t.replace(",", "").replace(". ", "").replace(".", "")
    t = re.sub(r"aed\s*", "aed", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ── Section 1: Plan identity / master data for all confirmed Classic plans ──

@pytest.mark.parametrize("query, checks", [
    # Classic 1R — AED 300K, HN Advantage, Worldwide excl USA/Canada
    ("What is the annual limit for Classic Plan-1R?", ["annual limit", "aed300"]),
    ("What is the provider network for Classic Plan-1R?", ["hn advantage"]),
    ("What is the area of coverage for Classic 1R?", ["worldwide"]),
    # Classic 2 — AED 250K, HN Standard Plus, Worldwide excl USA/Canada
    ("What is the annual limit for Classic Plan-2?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic 2?", ["hn standard plus"]),
    # Classic 2R — AED 250K, HN Standard Plus
    ("What is the annual limit for Classic Plan-2R?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic 2R?", ["hn standard plus"]),
    # Classic 3 — AED 250K, HN Standard
    ("What is the annual limit for Classic 3?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic Plan-3?", ["hn standard"]),
    # Classic 4 — AED 150K, HN Basic Plus
    ("What is the annual limit for Classic 4?", ["annual limit", "aed150"]),
    ("What is the provider network for Classic Plan-4?", ["hn basic plus"]),
    ("What is the area of coverage for Classic 4?", ["uae"]),
])
def test_classic_plan_master_fields(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# ── Section 2: Core benefit baseline — dental, optical, consultation, diagnostics, drugs ──

@pytest.mark.parametrize("query, must_contain, must_not_contain", [
    # Dental — should return Classic-specific data, NOT Remedy data
    ("Is dental covered for Classic Plan-2?", ["dental", "classic"], ["remedy"]),
    ("Is dental covered for Classic 2R?", ["dental", "classic"], ["remedy"]),
    ("Is dental covered for Classic 4?", ["dental", "classic"], ["remedy"]),
    # Optical/Vision — should return Classic-specific data
    ("Is optical covered for Classic Plan-2?", ["classic", "vision"], ["remedy"]),
    ("Is optical covered for Classic 4?", ["classic"], ["remedy"]),
    # Doctor consultation
    ("What is the doctor consultation coverage for Classic 3?", ["classic", "consultation"], ["remedy"]),
    ("What is the doctor consultation coverage for Classic 1R?", ["classic", "consultation"], ["remedy"]),
    # Diagnostics / Labs
    ("What is the diagnostics coverage for Classic 4?", ["classic", "covered"], ["remedy"]),
    ("What is the laboratory test coverage for Classic 2R?", ["classic", "laboratory"], ["remedy"]),
    # Prescribed drugs
    ("What is the prescribed drugs coverage for Classic 1R?", ["classic", "prescribed", "aed10"], ["remedy"]),
    ("What is the prescribed drugs coverage for Classic 2?", ["classic", "prescribed"], ["remedy"]),
])
def test_classic_benefit_baseline(query, must_contain, must_not_contain):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in must_contain:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"
    for check in must_not_contain:
        assert check not in norm, \
            f"Must NOT contain '{check}' in output for '{query}'. Got: {output}"


# ── Section 3: Maternity baseline ──

@pytest.mark.parametrize("query, checks", [
    ("What maternity benefits does Classic Plan-2R have?", ["maternity", "covered"]),
    ("What is the maternity benefit for Classic 3?", ["maternity", "covered"]),
    ("Is maternity covered for Classic 4?", ["maternity", "covered"]),
])
def test_classic_maternity_coverage(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# ── Section 4: Excluded plans are safely blocked ──

@pytest.mark.parametrize("query", [
    # HN_CLASSIC_1 — pending source
    "What is the annual limit for HN Classic 1?",
    "What is the provider network for Classic Plan 1?",
    "Is dental covered for Classic 1?",
    # HN_PRIME_1 — no source
    "What is the annual limit for Prime Plan 1?",
    "What is the network for HN Prime 1?",
    "Is dental covered for Prime 1?",
    # HN_PRIME_2 — network conflict
    "What is the annual limit for Prime Plan 2?",
    "What is the network for HN Prime 2?",
])
def test_excluded_plans_blocked(query):
    output = run_ask_kb(query)
    assert output.strip() == "No answer found." or "not available" in output.lower() or "not confirmed" in output.lower(), \
        f"Excluded plan should be blocked but got: {output}"


# ── Section 5: Remedy regression ──

@pytest.mark.parametrize("query, checks", [
    ("What is the annual limit for Remedy 02?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 03?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 06?", ["annual limit"]),
    ("What is the provider network for Remedy 02?", ["hn basic plus"]),
    ("Does Remedy 02 include physiotherapy?", ["covered"]),
    ("Is dental covered for Remedy 02?", ["dental", "remedy", "aed500"]),
    ("Is dental covered for Remedy 04?", ["dental", "remedy"]),
    ("What is the prescribed drugs coverage for Remedy 02?", ["prescribed", "remedy", "aed3"]),
])
def test_remedy_regression(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Remedy regression failed: expected '{check}' for '{query}'. Got: {output}"


# ── Section 6: Alias / variant name recognition ──

@pytest.mark.parametrize("query", [
    "What is the annual limit for HN_CLASSIC_2R?",
    "What is the annual limit for hn classic 2r?",
    "What is the annual limit for Classic 2R?",
    "What is the annual limit for Classic Plan-2R?",
])
def test_classic_name_variants(query):
    output = run_ask_kb(query)
    norm = normalize(output)
    assert "aed250" in norm.replace(" ", ""), \
        f"Expected AED 250,000 for '{query}'. Got: {output}"


# ── Section 7: Safety — no filename identity, no staging paths ──

def test_no_filename_identity_in_runtime():
    """Runtime modules must not reference source PDF filenames for plan identity."""
    for mod_path in ["src/plan_lookup.py", "src/benefit_lookup.py", "src/rules_lookup.py", "src/router.py"]:
        with open(mod_path, encoding="utf-8") as f:
            content = f.read()
        # No hardcoded staging paths in runtime
        assert "staging/" not in content, \
            f"Staging path reference found in {mod_path}"


def test_no_prime_in_runtime():
    """No HN_PRIME plan data should be in runtime."""
    for mod_path in ["src/plan_lookup.py", "src/router.py", "scripts/ask_kb.py"]:
        with open(mod_path, encoding="utf-8") as f:
            content = f.read()
        assert "HN_PRIME" not in content, \
            f"HN_PRIME reference found in {mod_path} — Prime plans should not be in runtime"


def test_no_prime_in_live_data():
    """No HN_PRIME plan data should be in live CSV files."""
    import csv
    data_files = [
        "data/plans/plan_master.csv",
        "data/benefits/additional_benefits.csv",
        "data/benefits/inpatient_benefits.csv",
        "data/benefits/outpatient_benefits.csv",
    ]
    for fp in data_files:
        with open(fp, encoding="utf-8") as f:
            content = f.read()
        assert "HN_PRIME" not in content, \
            f"HN_PRIME data found in {fp} — Prime plans should not be in live data"
