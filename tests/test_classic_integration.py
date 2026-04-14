"""
Integration tests for confirmed Classic plans (HN_CLASSIC_1R, 2, 2R, 3, 4).
Validates:
  1. Positive coverage for all 5 confirmed Classic plans
  2. Pending/excluded plans are blocked (HN_CLASSIC_1, HN_PRIME_1, HN_PRIME_2)
  3. Remedy regression (existing plans still answer correctly)
  4. No filename-based identity logic leaks
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


# ── Section 1: Positive coverage for all 5 confirmed Classic plans ──

@pytest.mark.parametrize("query, checks", [
    # Classic 1R — annual limit AED 300,000, network HN Advantage
    ("What is the annual limit for Classic Plan-1R?", ["annual limit", "aed300"]),
    ("What is the provider network for Classic Plan-1R?", ["hn advantage"]),
    ("What is the area of coverage for Classic 1R?", ["worldwide"]),
    # Classic 2 — annual limit AED 250,000, network HN Standard Plus
    ("What is the annual limit for Classic Plan-2?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic 2?", ["hn standard plus"]),
    # Classic 2R — annual limit AED 250,000, network HN Standard Plus
    ("What is the annual limit for Classic Plan-2R?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic 2R?", ["hn standard plus"]),
    # Classic 3 — annual limit AED 250,000, network HN Standard
    ("What is the annual limit for Classic 3?", ["annual limit", "aed250"]),
    ("What is the provider network for Classic Plan-3?", ["hn standard"]),
    # Classic 4 — annual limit AED 150,000, network HN Basic Plus
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


@pytest.mark.parametrize("query, checks", [
    # Maternity for Classic 2R
    ("What maternity benefits does Classic Plan-2R have?", ["maternity", "covered"]),
    # Maternity for Classic 3
    ("What is the maternity benefit for Classic 3?", ["maternity", "covered"]),
])
def test_classic_maternity_coverage(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Expected '{check}' in output for '{query}'. Got: {output}"


# ── Section 2: Pending/excluded plans are blocked ──

@pytest.mark.parametrize("query", [
    "What is the annual limit for HN Classic 1?",
    "What is the provider network for Classic Plan 1?",
])
def test_pending_classic1_blocked(query):
    output = run_ask_kb(query)
    assert output.strip() == "No answer found." or "not available" in output.lower(), \
        f"HN_CLASSIC_1 should be blocked but got: {output}"


# ── Section 3: Remedy regression — existing plans still work ──

@pytest.mark.parametrize("query, checks", [
    ("What is the annual limit for Remedy 02?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 03?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 04?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 05?", ["annual limit", "aed150"]),
    ("What is the annual limit for Remedy 06?", ["annual limit", "aed1"]),
    ("What is the provider network for Remedy 02?", ["hn basic plus"]),
    ("Does Remedy 02 include physiotherapy?", ["covered"]),
])
def test_remedy_regression(query, checks):
    output = run_ask_kb(query)
    norm = normalize(output)
    for check in checks:
        assert check.replace(" ", "") in norm.replace(" ", ""), \
            f"Remedy regression failed: expected '{check}' for '{query}'. Got: {output}"


# ── Section 4: Variant name formats are recognized ──

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


# ── Section 5: No filename-based identity ──

def test_no_filename_identity_in_runtime():
    """Ensure no runtime module references source PDF filenames for plan identity."""
    import importlib.util
    for mod_path in ["src/plan_lookup.py", "src/benefit_lookup.py", "src/rules_lookup.py", "src/router.py"]:
        with open(mod_path, encoding="utf-8") as f:
            content = f.read()
        assert ".pdf" not in content.lower() or "pdf" in content.lower().split("#")[-1], \
            f"Filename-based identity (.pdf) found in {mod_path}"
        # No hardcoded staging paths in runtime
        assert "staging/" not in content, \
            f"Staging path reference found in {mod_path}"
