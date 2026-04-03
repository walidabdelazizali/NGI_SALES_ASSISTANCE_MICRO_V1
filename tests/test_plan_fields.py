import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_area_of_coverage():
    out = run_cli("What is the area of coverage for Remedy 02?")
    assert "Area of Coverage for REMEDY 02" in out or "Area of Coverage for Remedy 02" in out

def test_provider_network():
    out = run_cli("What is the provider network for Remedy 02?")
    assert "Provider Network for REMEDY 02" in out or "Provider Network for Remedy 02" in out

def test_copayment():
    out = run_cli("What is the copayment for Remedy 02?")
    assert "Copayment for REMEDY 02" in out or "Copayment for Remedy 02" in out

def test_maternity():
    out = run_cli("Does Remedy 02 include maternity?")
    assert "Maternity for REMEDY 02" in out or "Maternity for Remedy 02" in out

def test_declaration_requirements():
    # All supported variants for declaration requirements
    queries = [
        "What are the declaration requirements for Remedy 02?",
        "Does Remedy 02 require a declaration?",
        "Is a declaration required for Remedy 02?",
        "Declaration for Remedy 02",
        "Declaration requirements for Remedy 02",
        "Declaration needed for Remedy 02"
    ]
    for q in queries:
        out = run_cli(q)
        assert "Declaration Requirements for REMEDY 02" in out or "Declaration Requirements for Remedy 02" in out

def test_pre_existing_conditions():
    # All supported variants for pre-existing conditions
    queries = [
        "What is the pre-existing conditions for Remedy 02?",
        "What are the pre existing conditions for Remedy 02?",
        "Does Remedy 02 cover existing conditions?",
        "Preexisting conditions for Remedy 02",
        "Existing conditions for Remedy 02"
    ]
    for q in queries:
        out = run_cli(q)
        # Accept either the legacy label or the new owner-facing answer
        if (
            "Pre-existing Conditions for REMEDY 02" in out or
            "Pre-existing Conditions for Remedy 02" in out
        ):
            continue
        # Accept if the output contains both 'pre-existing' and 'chronic' and 'Remedy 02'
        if (
            "Remedy 02" in out and
            "pre-existing" in out.lower() and
            "chronic" in out.lower()
        ):
            continue
        # Accept if the output contains 'existing conditions' and 'Remedy 02'
        if (
            "Remedy 02" in out and "existing condition" in out.lower()
        ):
            continue
        assert False, f"Output did not match expected label or valid owner-facing answer. Got: {out}"
