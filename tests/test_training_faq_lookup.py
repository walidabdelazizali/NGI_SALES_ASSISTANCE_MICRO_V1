import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from training_faq_lookup import faq_lookup

def test_reimbursement():
    path = Path(__file__).parent.parent / "data" / "training" / "faq_master.jsonl"
    result = faq_lookup("Can Remedy member claim reimbursement?", path)
    assert result is not None
    assert "reimbursement" in result["question"].lower() or "reimbursement" in result["answer"].lower()

def test_mental_health_cap():
    path = Path(__file__).parent.parent / "data" / "training" / "faq_master.jsonl"
    result = faq_lookup("Is mental health 800 per visit?", path)
    assert result is not None
    assert "cap" in result["answer"].lower() or "total" in result["answer"].lower()

def test_maternity_waiting_period():
    path = Path(__file__).parent.parent / "data" / "training" / "faq_master.jsonl"
    result = faq_lookup("Is maternity 45 days from policy inception?", path)
    assert result is not None
    assert "sign" in result["answer"].lower() or "hdf" in result["answer"].lower()

def test_influenza_test_vs_vaccine():
    path = Path(__file__).parent.parent / "data" / "training" / "faq_master.jsonl"
    result = faq_lookup("Is influenza test covered because TOB says influenza covered?", path)
    assert result is not None
    assert "vaccine" in result["answer"].lower() or "test" in result["answer"].lower()
