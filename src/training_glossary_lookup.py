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
                if not all(k in obj for k in ["id", "term", "definition", "keywords", "category", "notes", "status"]):
                    continue
                if not isinstance(obj["keywords"], list):
                    continue
                results.append(obj)
            except Exception:
                continue
    return results

def glossary_lookup(term: str, kb_path: Path) -> Optional[Dict]:
    glossary = load_jsonl(kb_path)
    # Try to extract the likely glossary term from question-style queries
    import re
    # e.g., 'What is UCR?' -> 'ucr'
    m = re.match(r"\s*(what is|define|meaning of|explain term)\s+([\w\- ]+)[\?\.]?", term.lower())
    if m:
        candidate = m.group(2).strip().lower()
    else:
        candidate = term.lower().strip()
    for entry in glossary:
        if entry.get("status", "") != "active":
            continue
        if entry.get("term", "").lower() == candidate:
            return entry
        # Fallback: keyword match
        keywords = [k.lower() for k in entry.get("keywords", [])]
        if candidate in keywords:
            return entry
    return None
