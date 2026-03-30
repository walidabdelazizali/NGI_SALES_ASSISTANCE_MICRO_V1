import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"


def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_plan_label():
    out = run_cli("What is the annual limit for Remedy 02?")
    assert out.startswith("[PLAN] ")

def test_network_label():
    out = run_cli("Is Aster Qusais in network?")
    assert out.startswith("[NETWORK] ")

def test_faq_label():
    out = run_cli("Show me the FAQ for direct billing.")
    assert out.startswith("[FAQ] ")

def test_no_answer():
    out = run_cli("What is the annual limit for Aster Qusais?")
    assert out == "No answer found."
