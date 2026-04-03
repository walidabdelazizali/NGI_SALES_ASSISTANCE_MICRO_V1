from pathlib import Path

from training_faq_lookup import faq_lookup
from training_rules_lookup import rules_lookup
from training_glossary_lookup import glossary_lookup
from training_escalation_lookup import escalation_lookup

DATA_DIR = Path(__file__).parent.parent / "data" / "training"
FAQ_PATH = DATA_DIR / "faq_master.jsonl"
RULES_PATH = DATA_DIR / "rules_master.jsonl"
GLOSSARY_PATH = DATA_DIR / "glossary_master.jsonl"
ESCALATION_PATH = DATA_DIR / "escalation_matrix.jsonl"

def _phrase_in_query(phrases, query):
    q = query.lower()
    return any(phrase in q for phrase in phrases)

def _prefer_exact(query, candidates, field):
    q = query.lower().strip()
    for c in candidates:
        if c.get(field, "").lower().strip() == q:
            return c
    # fallback: best token overlap
    best = None
    best_score = 0
    q_tokens = set(q.split())
    for c in candidates:
        text = c.get(field, "").lower()
        score = len(q_tokens & set(text.split()))
        if score > best_score:
            best = c
            best_score = score
    return best

def route_training_query(query: str) -> dict:
    q = query.lower().strip()
    # 1. FAQ exact normalized match short-circuit (before any intent or scoring logic)
    from training_faq_lookup import load_jsonl as load_faq_jsonl
    faqs = load_faq_jsonl(FAQ_PATH)
    norm_q = q
    for f in faqs:
        if f.get("status", "") == "active" and f.get("question", "").lower().strip() == norm_q:
            return {"type": "faq", "result": f}

    # 2. Glossary intent (always check glossary first for these)
    glossary_phrases = ["what is ", "define ", "meaning of ", "explain term"]
    if _phrase_in_query(glossary_phrases, q):
        glossary = glossary_lookup(query, GLOSSARY_PATH)
        if glossary:
            return {"type": "glossary", "result": glossary}
        else:
            return {"type": None, "result": None}
    # 3. Escalation intent
    escalation_phrases = ["escalate", "special approval", "who should handle", "exception case"]
    if _phrase_in_query(escalation_phrases, q):
        escalation = escalation_lookup(query, ESCALATION_PATH)
        if escalation:
            return {"type": "escalation", "result": escalation}
        else:
            return {"type": None, "result": None}
    # 4. Rules intent
    rules_phrases = ["why rejected", "why declined", "not covered", "can it be approved", "is it covered", "why was", "why is"]
    if _phrase_in_query(rules_phrases, q):
        rule = rules_lookup(query, RULES_PATH)
        if rule:
            return {"type": "rule", "result": rule}
        else:
            return {"type": None, "result": None}

    # 5. FAQ scoring fallback
    faq = faq_lookup(query, FAQ_PATH)
    if faq:
        return {"type": "faq", "result": faq}

    # 6. Rule exact normalized match
    from training_rules_lookup import load_jsonl as load_rule_jsonl
    rules = load_rule_jsonl(RULES_PATH)
    for r in rules:
        if r.get("status", "") == "active" and r.get("rule_name", "").lower().strip() == norm_q:
            return {"type": "rule", "result": r}

    # 7. Rule scoring fallback
    rule = rules_lookup(query, RULES_PATH)
    if rule:
        return {"type": "rule", "result": rule}

    # 8. Glossary fallback
    glossary = glossary_lookup(query, GLOSSARY_PATH)
    if glossary:
        return {"type": "glossary", "result": glossary}

    # 9. Escalation fallback
    escalation = escalation_lookup(query, ESCALATION_PATH)
    if escalation:
        return {"type": "escalation", "result": escalation}

    return {"type": None, "result": None}
