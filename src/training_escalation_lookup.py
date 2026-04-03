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
                if not all(k in obj for k in ["id", "case_name", "criteria", "action", "owner", "keywords", "category", "notes", "status"]):
                    continue
                if not isinstance(obj["keywords"], list):
                    continue
                results.append(obj)
            except Exception:
                continue
    return results

def escalation_lookup(criteria: str, kb_path: Path) -> Optional[Dict]:
    matrix = load_jsonl(kb_path)
    criteria_lc = criteria.lower()
    for entry in matrix:
        if entry.get("status", "") != "active":
            continue
        # 1. Match by case_name substring
        if entry.get("case_name", "").lower() in criteria_lc or criteria_lc in entry.get("case_name", "").lower():
            return entry
        # 2. Match by criteria substring
        if entry.get("criteria", "").lower() in criteria_lc or criteria_lc in entry.get("criteria", "").lower():
            return entry
        # 3. Match by keyword substring
        for kw in entry.get("keywords", []):
            if kw.lower() in criteria_lc or criteria_lc in kw.lower():
                return entry
    return None
