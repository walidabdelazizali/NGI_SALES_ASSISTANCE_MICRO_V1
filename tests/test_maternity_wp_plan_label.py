"""Regression test: maternity waiting period must return the explicitly requested plan.

Root cause (fixed): plan_lookup.py's waiting-period handler iterated the CSV
and returned the first matching row regardless of which plan was requested.
Since REMEDY_03 appeared first in maternity_benefits.csv, every query returned
"Remedy 03" even when R05 or R06 was explicitly asked.

Fix: filter by matched_row.get('plan_id') so the correct plan's row is returned.
"""
import subprocess
import sys
import pytest


def run_ask_kb(query):
    result = subprocess.run(
        [sys.executable, "scripts/ask_kb.py", query],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


@pytest.mark.parametrize("plan_num,plan_label", [
    ("02", "Remedy 02"),
    ("03", "Remedy 03"),
    ("04", "Remedy 04"),
    ("05", "Remedy 05"),
    ("06", "Remedy 06"),
])
def test_maternity_waiting_period_returns_correct_plan(plan_num, plan_label):
    """Each plan's maternity waiting period query must mention that plan's name."""
    output = run_ask_kb(f"What is the maternity waiting period for Remedy {plan_num}?")
    lower = output.lower()
    assert "nil" in lower, f"Expected 'nil' in output for Remedy {plan_num}. Got: {output}"
    assert plan_label.lower() in lower, (
        f"Expected '{plan_label}' in output but got wrong plan label. Output: {output}"
    )


@pytest.mark.parametrize("plan_num,wrong_plan", [
    ("05", "remedy 03"),
    ("06", "remedy 03"),
    ("04", "remedy 03"),
    ("02", "remedy 03"),
])
def test_maternity_waiting_period_no_wrong_plan(plan_num, wrong_plan):
    """Waiting period for plan X must NOT mention a different plan."""
    output = run_ask_kb(f"What is the maternity waiting period for Remedy {plan_num}?")
    lower = output.lower()
    if plan_num != wrong_plan.split()[-1]:
        assert wrong_plan not in lower, (
            f"Remedy {plan_num} waiting period leaked '{wrong_plan}'. Output: {output}"
        )
