import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_deductible():
    assert "AED 1,000" in run_cli("What is the deductible for Remedy 02?")
    assert "Remedy 04" in run_cli("What is the deductible for Remedy 04?")

def test_outpatient_coverage():
    assert "General OP" in run_cli("What outpatient coverage does Remedy 02 have?")
    assert "General OP" in run_cli("What outpatient coverage does Remedy 04 have?")
    assert "General OP" in run_cli("What outpatient coverage does Remedy 05 have?")

def test_inpatient_coverage():
    assert "All IP incl. surgery" in run_cli("What inpatient coverage does Remedy 02 have?")
    assert "All IP incl. surgery" in run_cli("What inpatient coverage does Remedy 04 have?")
    assert "All IP incl. surgery" in run_cli("What inpatient coverage does Remedy 06 have?")
    assert run_cli("What inpatient coverage does Remedy 07 have?") == "No answer found."

def test_emergency_coverage():
    assert "Covered in UAE and abroad" in run_cli("What emergency coverage does Remedy 02 have?")
    assert "Covered in UAE and abroad" in run_cli("What emergency coverage does Remedy 04 have?")
    assert "Covered in UAE and abroad" in run_cli("What emergency coverage does Remedy 06 have?")
    assert run_cli("What emergency coverage does Remedy 07 have?") == "No answer found."

def test_pharmacy_coverage():
    assert "AED 5,000" in run_cli("What pharmacy coverage does Remedy 02 have?")
    assert "AED 7,500" in run_cli("What pharmacy coverage does Remedy 04 have?")
    assert "AED 7,500" in run_cli("What pharmacy coverage does Remedy 05 have?")
    assert "AED 10,000" in run_cli("What pharmacy coverage does Remedy 06 have?")

def test_telemedicine():
    assert "Not covered" in run_cli("Does Remedy 02 include telemedicine?")
    assert "ISA Assist" in run_cli("Does Remedy 04 include telemedicine?")
    assert "ISA Assist" in run_cli("Does Remedy 06 include telemedicine?")
    assert run_cli("Does Remedy 07 include telemedicine?") == "No answer found."

def test_wellness_benefits():
    assert "Annual checkup included" in run_cli("Does Remedy 02 include wellness?")
    assert "Annual checkup" in run_cli("Does Remedy 04 include wellness?")
    assert "Annual checkup" in run_cli("Does Remedy 05 include wellness?")
    assert "Annual checkup" in run_cli("Does Remedy 06 include wellness?")
    assert run_cli("Does Remedy 07 include wellness?") == "No answer found."
