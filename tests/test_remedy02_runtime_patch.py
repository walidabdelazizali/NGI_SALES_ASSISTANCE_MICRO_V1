import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ask_kb.py"

def run_cli(question):
    result = subprocess.run([sys.executable, str(SCRIPT), question], capture_output=True, text=True)
    return result.stdout.strip()

def test_remedy02_benefit_and_rule_coverage():
    # 1. Physiotherapy
    assert "physio" in run_cli("Does Remedy 02 include physiotherapy?").lower()
    # 2. Maternity waiting period
    assert "waiting period" in run_cli("What is the maternity waiting period for Remedy 02?").lower()
    # 3. Dental
    assert "dental" in run_cli("Does Remedy 02 include dental?").lower()
    # 4. GP referral
    assert "referral" in run_cli("Do I need GP referral for specialist consultation in Remedy 02?").lower()
    # 5. Pre-existing condition rules
    assert "pre-existing" in run_cli("What are the pre-existing condition rules for Remedy 02?").lower()
    # 6. Telemedicine distinction
    out = run_cli("Does Remedy 02 include telemedicine?").lower()
    assert "telemedicine" in out and ("not covered" in out or "isa assist" in out)
