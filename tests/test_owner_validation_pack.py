import json
import subprocess
import sys
from pathlib import Path
import pytest

DATASET = Path(__file__).parent / "fixtures" / "owner_validation_queries.json"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

with open(DATASET, encoding="utf-8") as f:
    CASES = json.load(f)

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

@pytest.mark.parametrize("case", CASES)
def test_owner_validation(case):
    out = run_cli(case["query"])
    if case["expected_behavior"] == "answer":
        assert out != "No answer found.", f"Expected answer for: {case['query']}"
        if "expected_contains" in case:
            assert case["expected_contains"].lower() in out.lower(), f"Output did not contain expected text for: {case['query']}"
    elif case["expected_behavior"] == "gap_check":
        assert out == "No answer found." or "not supported" in out.lower(), f"Expected gap for: {case['query']}"
    elif case["expected_behavior"] == "answer_or_gap":
        # Accept either a valid answer or a gap
        if out == "No answer found.":
            assert True
        else:
            if "expected_contains" in case:
                assert case["expected_contains"].lower() in out.lower(), f"Output did not contain expected text for: {case['query']}"
    else:
        # Unknown behavior, fail
        assert False, f"Unknown expected_behavior: {case['expected_behavior']} for {case['query']}"
