import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from training_router import route_training_query

def test_glossary_ucr():
    result = route_training_query("What is UCR?")
    assert result["type"] == "glossary"
    assert "ucr" in result["result"]["term"].lower()

def test_faq_reimbursement():
    result = route_training_query("Can Remedy member claim reimbursement?")
    assert result["type"] in ("faq", "rule")
    assert "reimbursement" in str(result["result"]).lower()

def test_mental_health_cap():
    result = route_training_query("Is mental health 800 per visit?")
    assert result["type"] == "faq"
    assert "cap" in result["result"]["answer"].lower() or "total" in result["result"]["answer"].lower()

def test_maternity_waiting_period():
    result = route_training_query("Is maternity 45 days from policy inception?")
    assert result["type"] in ("faq", "rule")
    assert "sign" in result["result"]["answer"].lower() or "hdf" in result["result"]["answer"].lower()

def test_influenza_test_vs_vaccine():
    result = route_training_query("Is influenza test covered because TOB says influenza covered?")
    assert result["type"] == "faq"
    assert "vaccine" in result["result"]["answer"].lower() or "test" in result["result"]["answer"].lower()

def test_dental_out_of_network():
    result = route_training_query("Why was dental treated as out of network?")
    assert result["type"] in ("faq", "rule")
    assert "essential partner" in result["result"]["answer"].lower() or "restricted" in result["result"]["answer"].lower()

def test_escalation_special_approval():
    result = route_training_query("Who should handle a special approval exception?")
    assert result["type"] == "escalation"
    assert "owner" in result["result"]

def test_unknown_ambiguous():
    result = route_training_query("What is the meaning of life?")
    assert result["type"] is None
    assert result["result"] is None
