from __future__ import annotations

import csv
import re
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "faq" / "training_questions_master.csv"


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _token_set(value: str) -> set[str]:
    return {token for token in _normalize(value).split() if token}


def _load_rows() -> list[dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def lookup_faq(query: str) -> dict[str, str]:
    normalized_query = _normalize(query)
    query_tokens = _token_set(query)
    rows = _load_rows()

    for row in rows:
        if _normalize(row["question"]) == normalized_query:
            return {
                "status": "found",
                "route": "faq_lookup",
                "question_id": row["question_id"],
                "matched_question": row["question"],
                "answer": row["answer"],
                "category": row["category"],
            }

    best_row: dict[str, str] | None = None
    best_score = 0

    for row in rows:
        row_tokens = _token_set(" ".join([row["question"], row["category"], row["subcategory"]]))
        score = len(query_tokens & row_tokens)
        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 2:
        return {
            "status": "found",
            "route": "faq_lookup",
            "question_id": best_row["question_id"],
            "matched_question": best_row["question"],
            "answer": best_row["answer"],
            "category": best_row["category"],
        }

    return {
        "status": "not_found",
        "route": "faq_lookup",
        "message": "No FAQ match was found in training_questions_master.csv.",
    }