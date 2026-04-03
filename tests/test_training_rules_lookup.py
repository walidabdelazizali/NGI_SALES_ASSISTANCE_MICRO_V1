import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from training_rules_lookup import rules_lookup

def test_maternity_waiting_period_rule():
    path = Path(__file__).parent.parent / "data" / "training" / "rules_master.jsonl"
    result = rules_lookup("Is maternity 45 days from policy inception?", path)
    assert result is not None
    assert "sign" in result["answer"].lower() or "hdf" in result["answer"].lower()

def test_dental_out_of_network():
    path = Path(__file__).parent.parent / "data" / "training" / "rules_master.jsonl"
    result = rules_lookup("Why was dental treated as out of network?", path)
    assert result is not None
    assert "essential partner" in result["answer"].lower() or "restricted" in result["answer"].lower()
