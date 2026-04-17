"""
Tests for centralized plan alias policy.
Validates:
  1. Confirmed plan names resolve correctly
  2. Rejected / excluded names stay rejected
  3. No unsafe fallback (Classic 1 → Classic 1R, Prime → Remedy)
  4. Integration: ask_kb routes correctly through the policy
"""
import subprocess
import sys
import pytest

# ── Direct unit tests on resolve_plan_alias ──

sys.path.insert(0, "src")
from plan_alias_policy import resolve_plan_alias, CONFIRMED_CLASSIC_IDS, CONFIRMED_REMEDY_IDS


# Section 1: Confirmed Classic plans resolve correctly

@pytest.mark.parametrize("query, expected_id", [
    ("classic 1r", "HN_CLASSIC_1R"),
    ("classic plan 1r", "HN_CLASSIC_1R"),
    ("hn classic 1r", "HN_CLASSIC_1R"),
    ("hn_classic_1r", "HN_CLASSIC_1R"),
    ("Classic Plan-1R", "HN_CLASSIC_1R"),
    ("classic 2", "HN_CLASSIC_2"),
    ("classic plan 2", "HN_CLASSIC_2"),
    ("classic 2r", "HN_CLASSIC_2R"),
    ("hn classic 2r", "HN_CLASSIC_2R"),
    ("classic 3", "HN_CLASSIC_3"),
    ("classic plan 3", "HN_CLASSIC_3"),
    ("classic 4", "HN_CLASSIC_4"),
    ("hn_classic_4", "HN_CLASSIC_4"),
])
def test_confirmed_classic_resolves(query, expected_id):
    plan_id, status = resolve_plan_alias(query)
    assert status == "confirmed", f"Expected 'confirmed' for '{query}', got '{status}'"
    assert plan_id == expected_id, f"Expected '{expected_id}' for '{query}', got '{plan_id}'"


# Section 2: Confirmed Remedy plans resolve correctly

@pytest.mark.parametrize("query, expected_id", [
    ("remedy 02", "REMEDY_02"),
    ("remedy_03", "REMEDY_03"),
    ("remedy-04", "REMEDY_04"),
    ("remedy05", "REMEDY_05"),
    ("remedy 06", "REMEDY_06"),
])
def test_confirmed_remedy_resolves(query, expected_id):
    plan_id, status = resolve_plan_alias(query)
    assert status == "confirmed", f"Expected 'confirmed' for '{query}', got '{status}'"
    assert plan_id == expected_id, f"Expected '{expected_id}' for '{query}', got '{plan_id}'"


# Section 3: Excluded plans are correctly rejected

@pytest.mark.parametrize("query, expected_status", [
    # Classic 1 must NOT resolve to Classic 1R
    ("classic 1", "excluded"),
    ("classic plan 1", "excluded"),
    ("hn classic 1", "excluded"),
    ("hn_classic_1", "excluded"),
    # Prime plans — all excluded
    ("prime 1", "excluded"),
    ("prime 2", "excluded"),
    ("hn prime 1", "excluded"),
    ("hn_prime_2", "excluded"),
    ("prime plan 1", "excluded"),
])
def test_excluded_plans_rejected(query, expected_status):
    plan_id, status = resolve_plan_alias(query)
    assert status == expected_status, f"Expected '{expected_status}' for '{query}', got '{status}' (plan_id={plan_id})"
    # Must NOT be any confirmed plan
    assert plan_id not in CONFIRMED_CLASSIC_IDS, f"Excluded '{query}' must not resolve to confirmed Classic"
    assert plan_id not in CONFIRMED_REMEDY_IDS, f"Excluded '{query}' must not resolve to Remedy"


# Section 4: Classic 1 must NEVER resolve to Classic 1R

def test_classic_1_never_resolves_to_1r():
    """Critical safety: 'Classic 1' must not accidentally match 'Classic 1R'."""
    for q in ("classic 1", "hn classic 1", "classic plan 1", "hn_classic_1"):
        plan_id, status = resolve_plan_alias(q)
        assert plan_id != "HN_CLASSIC_1R", f"CRITICAL: '{q}' must not resolve to HN_CLASSIC_1R"
        assert status == "excluded"


# Section 5: Unrecognized Remedy plans blocked

@pytest.mark.parametrize("query", [
    "remedy 01",
    "remedy 07",
    "remedy 10",
    "remedy 99",
])
def test_unrecognized_remedy_blocked(query):
    plan_id, status = resolve_plan_alias(query)
    assert status == "unrecognized_remedy", f"Expected 'unrecognized_remedy' for '{query}', got '{status}'"


# Section 6: Queries with no plan family → unknown

@pytest.mark.parametrize("query", [
    "what is dental coverage",
    "how much is the copay",
    "مرحبا",
])
def test_no_plan_family_returns_unknown(query):
    plan_id, status = resolve_plan_alias(query)
    assert status == "unknown"
    assert plan_id is None


# ── Integration tests via ask_kb ──

def run_ask_kb(query):
    result = subprocess.run(
        [sys.executable, "scripts/ask_kb.py", query],
        capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


# Section 7: Integration — confirmed plans answer correctly

@pytest.mark.parametrize("query, must_contain", [
    ("What is the annual limit for Classic Plan-1R?", "300"),
    ("What network does Classic 2 use?", "standard plus"),
    ("Is dental covered for Classic Plan-2?", "classic"),
    ("What is the annual limit for Remedy 02?", "150"),
    ("Is dental covered for Remedy 02?", "remedy"),
])
def test_integration_confirmed_answers(query, must_contain):
    output = run_ask_kb(query)
    assert must_contain.lower() in output.lower(), f"Expected '{must_contain}' in output for '{query}'. Got: {output}"


# Section 8: Integration — excluded plans blocked (no Remedy fallback)

@pytest.mark.parametrize("query", [
    "Is dental covered for Classic 1?",
    "Is dental covered for Prime 1?",
    "What is the annual limit for Prime 2?",
    "What network does Classic 1 use?",
    "What is the annual limit for HN Classic 1?",
])
def test_integration_excluded_blocked(query):
    output = run_ask_kb(query)
    assert output == "No answer found.", f"Excluded query should be blocked but got: {output}"
    assert "remedy" not in output.lower(), f"Excluded query must not fall back to Remedy: {output}"
