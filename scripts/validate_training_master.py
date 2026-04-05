import json
import os
from collections import Counter

ALLOWED_CATEGORIES = [
    "benefit", "rule", "approval", "network", "reimbursement", "exclusion", "underwriting", "escalation", "glossary", "sales_pitch", "client_reply"
]
ALLOWED_LANGS = ["en", "ar"]
REQUIRED_FIELDS = ["id", "plan_id", "lang", "category", "question", "answer", "keywords", "source", "intent", "owner_note"]


def validate_training_master(path):
    errors = []
    seen_ids = set()
    seen_qpl = set()  # (question, plan_id, lang)
    category_counts = Counter()
    lang_counts = Counter()
    total = 0
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                errors.append(f"Line {i}: Invalid JSON: {e}")
                continue
            total += 1
            # Required fields
            for field in REQUIRED_FIELDS:
                if field not in rec:
                    errors.append(f"Line {i}: Missing required field: {field}")
            # Unique id
            rid = rec.get("id")
            if rid in seen_ids:
                errors.append(f"Line {i}: Duplicate id: {rid}")
            seen_ids.add(rid)
            # Allowed category
            cat = rec.get("category")
            if cat not in ALLOWED_CATEGORIES:
                errors.append(f"Line {i}: Invalid category: {cat}")
            else:
                category_counts[cat] += 1
            # Allowed lang
            lang = rec.get("lang")
            if lang not in ALLOWED_LANGS:
                errors.append(f"Line {i}: Invalid lang: {lang}")
            else:
                lang_counts[lang] += 1
            # Non-empty question/answer
            if not rec.get("question"):
                errors.append(f"Line {i}: Empty question")
            if not rec.get("answer"):
                errors.append(f"Line {i}: Empty answer")
            # Duplicate (question, plan_id, lang)
            qpl = (rec.get("question"), rec.get("plan_id"), rec.get("lang"))
            if qpl in seen_qpl:
                errors.append(f"Line {i}: Duplicate question+plan_id+lang: {qpl}")
            seen_qpl.add(qpl)
    print(f"Validation complete. {total} records checked.")
    if errors:
        print(f"Found {len(errors)} issues:")
        for e in errors:
            print(e)
    else:
        print("No validation errors found.")
    print("Category counts:", dict(category_counts))
    print("Language counts:", dict(lang_counts))

if __name__ == "__main__":
    validate_training_master(os.path.join(os.path.dirname(__file__), "..", "data", "training", "training_master.jsonl"))
