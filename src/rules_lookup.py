from __future__ import annotations

import csv
import re
from pathlib import Path


RULES_DIR = Path(__file__).resolve().parents[1] / "data" / "rules"
FILES = [
    "approvals_rules.csv",
    "referral_rules.csv",
    "reimbursement_rules.csv",
    "exclusions_master.csv",
    "terms_conditions.csv",
]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _token_set(value: str) -> set[str]:
    return {token for token in _normalize(value).split() if token}


def _load_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for file_name in FILES:
        path = RULES_DIR / file_name
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                row["section"] = file_name.replace(".csv", "")
                rows.append(row)
    return rows


def lookup_rules(query: str) -> dict[str, str]:
    query_tokens = _token_set(query)
    best_row: dict[str, str] | None = None
    best_score = 0

    for row in _load_rows():
        haystack = " ".join([row["topic"], row["rule_text"], row["applies_to"], row["section"]])
        score = len(query_tokens & _token_set(haystack))
        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 2:
        return {
            "status": "found",
            "route": "rules_lookup",
            "rule_id": best_row["rule_id"],
            "matched_topic": best_row["topic"],
            "answer": (
                f"{best_row['topic']} [{best_row['section']}]\n"
                f"{best_row['rule_text']}"
            ),
        }

    return {
        "status": "not_found",
        "route": "rules_lookup",
        "message": "No rule match was found in the rules CSV files.",
    }