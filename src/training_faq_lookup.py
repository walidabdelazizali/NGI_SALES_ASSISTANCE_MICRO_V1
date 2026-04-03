import json
from pathlib import Path
from typing import List, Dict, Optional

def load_jsonl(path: Path) -> List[Dict]:
    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Check for required fields in new schema
                if not all(k in obj for k in ["id", "question", "answer", "keywords", "category", "sub_category", "notes", "status"]):
                    continue
                if not isinstance(obj["keywords"], list):
                    continue
                results.append(obj)
            except Exception:
                continue
    return results

def faq_lookup(query: str, kb_path: Path) -> Optional[Dict]:
    faqs = load_jsonl(kb_path)
    def normalize(text):
        return " ".join(text.lower().strip().split())
    query_norm = normalize(query)
    # 1. Exact normalized question match
    for faq in faqs:
        if faq.get("status", "") != "active":
            continue
        q_norm = normalize(faq.get("question", ""))
        if query_norm == q_norm:
            return faq
    # 2. Strong phrase-priority for reimbursement
    reimbursement_phrases = [
        "remedy member claim reimbursement",
        "claim reimbursement",
        "reimbursement"
    ]
    if any(phrase in query_norm for phrase in reimbursement_phrases):
        for phrase in reimbursement_phrases:
            for faq in faqs:
                if faq.get("status", "") != "active":
                    continue
                q_norm = normalize(faq.get("question", ""))
                keywords = [normalize(k) for k in faq.get("keywords", [])]
                if phrase in q_norm or any(phrase in k for k in keywords):
                    return faq
    # 3. Fallback to previous scoring logic
    best = None
    best_score = -1
    for faq in faqs:
        if faq.get("status", "") != "active":
            continue
        q = faq.get("question", "").lower().strip()
        keywords = [k.lower() for k in faq.get("keywords", [])]
        # Query is full substring in question
        if query_norm in normalize(q):
            score = 80
        # All query tokens in question
        elif all(word in q for word in query_norm.split()):
            score = 60
        # All query tokens in keywords
        elif all(word in keywords for word in query_norm.split()):
            score = 50
        # Any keyword overlap
        elif any(word in keywords for word in query_norm.split()):
            score = 30 + sum(1 for word in query_norm.split() if word in keywords)
        # Any token overlap in question
        else:
            score = sum(1 for word in query_norm.split() if word in q)
        if score > best_score:
            best = faq
            best_score = score
    return best if best_score > 0 else None
