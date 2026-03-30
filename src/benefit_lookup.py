from __future__ import annotations

import csv
import re
from pathlib import Path


BENEFIT_DIR = Path(__file__).resolve().parents[1] / "data" / "benefits"
FILES = [
    "inpatient_benefits.csv",
    "outpatient_benefits.csv",
    "preventive_benefits.csv",
    "additional_benefits.csv",
    "maternity_benefits.csv",
    "isa_assist_benefits.csv",
]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _token_set(value: str) -> set[str]:
    return {token for token in _normalize(value).split() if token}


def _load_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for file_name in FILES:
        path = BENEFIT_DIR / file_name
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                row["section"] = file_name.replace("_benefits.csv", "")
                rows.append(row)
    return rows


def lookup_benefit(query: str) -> dict[str, str]:
    query_tokens = _token_set(query)
    best_row: dict[str, str] | None = None
    best_score = 0

    for row in _load_rows():
        haystack = " ".join([row["plan_id"], row["plan_name"], row["benefit_name"], row["section"]])
        score = len(query_tokens & _token_set(haystack))
        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 2:
        return {
            "status": "found",
            "route": "benefit_lookup",
            "benefit_id": best_row["benefit_id"],
            "matched_benefit": best_row["benefit_name"],
            "answer": (
                f"{best_row['benefit_name']} [{best_row['section']}] for {best_row['plan_name']}\n"
                f"Coverage: {best_row['coverage']}"
            ),
        }

    return {
        "status": "not_found",
        "route": "benefit_lookup",
        "message": "No benefit match was found in the benefit CSV files.",
    }