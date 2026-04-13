import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_annual_limit_multiple():
    assert "150,000" in run_cli("What is the annual limit for Remedy 04?")
    assert "150,000" in run_cli("What is the annual limit for Remedy 05?")
    assert "150,000" in run_cli("What is the annual limit for Remedy 06?")
    assert run_cli("What is the annual limit for Remedy 07?") == "No answer found."

def test_area_of_coverage_multiple():
    assert "Remedy 04" in run_cli("What is the area of coverage for Remedy 04?")
    assert "Remedy 05" in run_cli("What is the area of coverage for Remedy 05?")
    assert "Remedy 06" in run_cli("What is the area of coverage for Remedy 06?")
    assert run_cli("What is the area of coverage for Remedy 07?") == "No answer found."

def test_provider_network_multiple():
    assert "Remedy 04" in run_cli("What is the provider network for Remedy 04?")
    assert "Remedy 05" in run_cli("What is the provider network for Remedy 05?")
    assert "Remedy 06" in run_cli("What is the provider network for Remedy 06?")
    assert run_cli("What is the provider network for Remedy 07?") == "No answer found."

def test_copayment_multiple():
    assert "Remedy 04" in run_cli("What is the copayment for Remedy 04?")
    assert "Remedy 05" in run_cli("What is the copayment for Remedy 05?")
    assert "Remedy 06" in run_cli("What is the copayment for Remedy 06?")
    assert run_cli("What is the copayment for Remedy 07?") == "No answer found."

def test_maternity_and_declaration_multiple():
    assert "Remedy 04" in run_cli("Does Remedy 04 include maternity?")
    assert "Remedy 04" in run_cli("What are the declaration requirements for Remedy 04?")
    assert "Remedy 05" in run_cli("Does Remedy 05 include maternity?")
    assert "Remedy 05" in run_cli("What are the declaration requirements for Remedy 05?")
    assert "Remedy 06" in run_cli("Does Remedy 06 include maternity?")
    assert "Remedy 06" in run_cli("What are the declaration requirements for Remedy 06?")
    assert run_cli("Does Remedy 07 include maternity?") == "No answer found."
    assert run_cli("What are the declaration requirements for Remedy 07?") == "No answer found."
