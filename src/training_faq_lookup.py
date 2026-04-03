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
    query_lc = query.lower().strip()
    best = None
    best_score = -1
    for faq in faqs:
        if faq.get("status", "") != "active":
            continue
        q = faq.get("question", "").lower().strip()
        keywords = [k.lower() for k in faq.get("keywords", [])]
        # 1. Exact question match
        if query_lc == q:
            score = 100
        # 2. Query is full substring in question
        elif query_lc in q:
            score = 80
        # 3. All query tokens in question
        elif all(word in q for word in query_lc.split()):
            score = 60
        # 4. All query tokens in keywords
        elif all(word in keywords for word in query_lc.split()):
            score = 50
        # 5. Any keyword overlap
        elif any(word in keywords for word in query_lc.split()):
            score = 30 + sum(1 for word in query_lc.split() if word in keywords)
        # 6. Any token overlap in question
        else:
            score = sum(1 for word in query_lc.split() if word in q)
        if score > best_score:
            best = faq
            best_score = score
    return best if best_score > 0 else None
