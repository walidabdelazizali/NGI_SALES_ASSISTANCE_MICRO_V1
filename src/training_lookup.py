import json
import os
from typing import List, Dict, Optional

TRAINING_FILE = os.path.join(os.path.dirname(__file__), '../data/training/training_master.jsonl')

REQUIRED_FIELDS = [
    'id', 'plan_id', 'lang', 'category', 'question', 'answer', 'keywords', 'source', 'intent'
]


def load_training_records() -> List[Dict]:
    """
    Loads and normalizes training records from the JSONL file.
    Skips malformed rows and ensures all required fields are present.
    """
    records = []
    with open(TRAINING_FILE, encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
                if not all(field in rec for field in REQUIRED_FIELDS):
                    continue
                # Normalize plan_id, lang, category to uppercase/lowercase as needed
                rec['plan_id'] = str(rec['plan_id']).upper()
                rec['lang'] = str(rec['lang']).lower()
                rec['category'] = str(rec['category']).lower()
                # Normalize keywords to list of lowercase strings
                if isinstance(rec.get('keywords'), list):
                    rec['keywords'] = [str(k).lower() for k in rec['keywords']]
                else:
                    rec['keywords'] = []
                records.append(rec)
            except Exception:
                continue  # skip malformed rows
    return records


def get_training_records_for_plan(plan_id: str) -> List[Dict]:
    """
    Returns all records for a given plan_id, including GLOBAL records.
    """
    plan_id = str(plan_id).upper()
    records = load_training_records()
    return [r for r in records if r['plan_id'] == plan_id or r['plan_id'] == 'GLOBAL']


def search_training_records(query: str, plan_id: Optional[str] = None, lang: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
    """
    Search records by keyword, question text, and optional filters.
    - query: matches if in question or in keywords
    - plan_id: includes GLOBAL records
    - lang: filter by language
    - category: filter by category
    """
    query = query.strip().lower() if query else ''
    plan_id = str(plan_id).upper() if plan_id else None
    lang = lang.lower() if lang else None
    category = category.lower() if category else None
    records = load_training_records()
    results = []
    for r in records:
        if plan_id and not (r['plan_id'] == plan_id or r['plan_id'] == 'GLOBAL'):
            continue
        if lang and r['lang'] != lang:
            continue
        if category and r['category'] != category:
            continue
        # Match query in question or keywords
        if query:
            if query in r['question'].lower() or any(query in k for k in r['keywords']):
                results.append(r)
        else:
            results.append(r)
    return results
