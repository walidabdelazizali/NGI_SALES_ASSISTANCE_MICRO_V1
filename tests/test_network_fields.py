import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_exact_provider_name():
    out = run_cli("Is Aster Hospital Qusais in the network?")
    assert "Aster Hospital Qusais is in network" in out

def test_alias_provider_name():
    out = run_cli("Is Aster Qs in the network?")
    assert "Aster Hospital Qusais is in network" in out

def test_provider_not_found():
    out = run_cli("Is Fake Hospital in the network?")
    assert "No answer found" in out

def test_direct_billing_yes():
    out = run_cli("Does Mediclinic City Hospital offer direct billing?")
    assert "Direct billing is available" in out

def test_direct_billing_no():
    out = run_cli("Does Thumbay Hospital offer direct billing?")
    assert "Direct billing is NOT available" in out
