import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_annual_limit_multiple():
    assert run_cli("What is the annual limit for Remedy 04?") == "No answer found."
    assert run_cli("What is the annual limit for Remedy 05?") == "No answer found."
    assert run_cli("What is the annual limit for Remedy 06?") == "No answer found."

def test_area_of_coverage_multiple():
    assert run_cli("What is the area of coverage for Remedy 04?") == "No answer found."
    assert run_cli("What is the area of coverage for Remedy 05?") == "No answer found."
    assert run_cli("What is the area of coverage for Remedy 06?") == "No answer found."

def test_provider_network_multiple():
    assert run_cli("What is the provider network for Remedy 04?") == "No answer found."
    assert run_cli("What is the provider network for Remedy 05?") == "No answer found."
    assert run_cli("What is the provider network for Remedy 06?") == "No answer found."

def test_copayment_multiple():
    assert run_cli("What is the copayment for Remedy 04?") == "No answer found."
    assert run_cli("What is the copayment for Remedy 05?") == "No answer found."
    assert run_cli("What is the copayment for Remedy 06?") == "No answer found."

def test_maternity_and_declaration_multiple():
    assert run_cli("Does Remedy 04 include maternity?") == "No answer found."
    assert run_cli("What are the declaration requirements for Remedy 04?") == "No answer found."
    assert run_cli("Does Remedy 05 include maternity?") == "No answer found."
    assert run_cli("What are the declaration requirements for Remedy 05?") == "No answer found."
    assert run_cli("Does Remedy 06 include maternity?") == "No answer found."
    assert run_cli("What are the declaration requirements for Remedy 06?") == "No answer found."
