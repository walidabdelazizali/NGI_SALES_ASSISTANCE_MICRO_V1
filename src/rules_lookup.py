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
    required_fields = ["topic", "rule_text", "applies_to"]
    for file_name in FILES:
        path = RULES_DIR / file_name
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                # Data hygiene: skip duplicate header rows
                if row.get('rule_id', '').lower() == 'rule_id' or row.get('topic', '').lower() == 'topic':
                    continue
                # Skip rows that are completely blank or missing required fields
                if not any(row.values()):
                    continue
                if any(f not in row or not row[f].strip() for f in required_fields):
                    continue
                row["section"] = file_name.replace(".csv", "")
                rows.append(row)
    return rows


def lookup_rules(query: str) -> dict[str, str]:
    query_tokens = _token_set(query)
    # --- Deterministic override for Remedy 03 referral-intent queries ---
    referral_intent_terms = ["gp referral", "specialist consultation", "specialist referral", "e-referral"]
    ql = query.lower()
    # Only treat as referral intent if not a generic approval query
    approval_terms = ["approval", "approvals", "pre-approval", "preapproval"]
    is_approval_query = any(term in ql for term in approval_terms)
    # If it's a generic approval query, route to approvals_rules
    if is_approval_query:
        rows = list(_load_rows())
        # 0. Prefer specific approval rule matching query tokens (e.g. MRI pre-approval for a specific plan)
        best_specific = None
        best_specific_score = 2
        for row in rows:
            if row["section"] == "approvals_rules":
                haystack = " ".join([row.get("topic", ""), row.get("rule_text", ""), row.get("applies_to", "")])
                score = len(query_tokens & _token_set(haystack))
                if score > best_specific_score:
                    best_specific_score = score
                    best_specific = row
        if best_specific:
            return {
                "status": "found",
                "route": "rules_lookup",
                "rule_id": best_specific["rule_id"],
                "matched_topic": best_specific["topic"],
                "answer": f"{best_specific['topic']}\n{best_specific['rule_text']}"
            }
        # 1. Prefer a general approval rule (topic contains 'approval', applies_to General training use)
        for row in rows:
            if row["section"] == "approvals_rules" and "approval" in row.get("topic", "").lower() and row.get("applies_to", "").strip().lower() == "general training use":
                return {
                    "status": "found",
                    "route": "rules_lookup",
                    "rule_id": row["rule_id"],
                    "matched_topic": row["topic"],
                    "answer": f"{row['topic']}\n{row['rule_text']}"
                }
        # 2. Fallback: any approvals_rules row with topic containing 'approval'
        for row in rows:
            if row["section"] == "approvals_rules" and "approval" in row.get("topic", "").lower():
                return {
                    "status": "found",
                    "route": "rules_lookup",
                    "rule_id": row["rule_id"],
                    "matched_topic": row["topic"],
                    "answer": f"{row['topic']}\n{row['rule_text']}"
                }
        # 3. Fallback: any approvals_rules row
        for row in rows:
            if row["section"] == "approvals_rules":
                return {
                    "status": "found",
                    "route": "rules_lookup",
                    "rule_id": row["rule_id"],
                    "matched_topic": row["topic"],
                    "answer": f"{row['topic']}\n{row['rule_text']}"
                }
        # If no approval rule found, return not_found
        return {
            "status": "not_found",
            "route": "rules_lookup",
            "message": "No approval rule found in approvals_rules."
        }
    referral_intent = (any(term in ql for term in referral_intent_terms) or ("specialist" in ql and "consultation" in ql)) and not is_approval_query
    if referral_intent and "remedy 03" in ql:
        rows = list(_load_rows())
        found_row = None
        for row in rows:
            if row["section"] == "referral_rules" and row.get("applies_to", "").strip() == "REMEDY_03":
                found_row = row
                break
        if found_row:
            return {
                "status": "found",
                "route": "rules_lookup",
                "rule_id": found_row["rule_id"],
                "matched_topic": found_row["topic"],
                "answer": f"{found_row['topic']}\n{found_row['rule_text']}"
            }

    best_row: dict[str, str] | None = None
    best_score = 0
    tied_rows = []

    for row in _load_rows():
        haystack = " ".join([row["topic"], row["rule_text"], row["applies_to"], row["section"]])
        score = len(query_tokens & _token_set(haystack))
        # MINI PATCH: boost score for pre-existing/chronic/undeclared/6 months matches in terms_conditions
        if row["section"] == "terms_conditions":
            if any(term in query.lower() for term in ["pre-existing", "chronic", "undeclared", "first 6 months"]):
                score += 2
        # PATCH: boost referral_rules.csv for GP referral/specialist queries
        if row["section"] == "referral_rules":
            # Targeted boost for GP referral/specialist queries
            referral_terms = ["gp referral", "specialist consultation", "specialist referral", "e-referral", "referral", "specialist"]
            if any(term in query.lower() for term in referral_terms):
                score += 6
            # PATCH: allow applies_to like 'REMEDY_02 through REMEDY_06' to match REMEDY_03
            if 'remedy 03' in query.lower() or 'remedy03' in query.lower() or 'ريمدي 03' in query.lower() or 'ريميدي 03' in query.lower() or '03' in query.lower():
                applies_to = row.get('applies_to', '').replace(' ', '').lower()
                if 'remedy_02throughremedy_06' in applies_to or 'remedy02throughremedy06' in applies_to:
                    score += 5
        if score > best_score:
            best_score = score
            tied_rows = [row]
        elif score == best_score and score > 0:
            tied_rows.append(row)

    # Winner selection: for GP referral/specialist queries under Remedy 03, prefer referral_rules.csv
    if tied_rows and best_score >= 2:
        if any(term in query.lower() for term in ["gp referral", "specialist consultation", "specialist referral", "e-referral"]) and "remedy 03" in query.lower():
            for row in tied_rows:
                if row["section"] == "referral_rules" and row.get("applies_to", "").strip() == "REMEDY_03":
                    best_row = row
                    break
        if not best_row:
            best_row = tied_rows[0]
        return {
            "status": "found",
            "route": "rules_lookup",
            "rule_id": best_row["rule_id"],
            "matched_topic": best_row["topic"],
            "answer": (
                f"{best_row['topic']}\n"
                f"{best_row['rule_text']}"
            ),
        }

    return {
        "status": "not_found",
        "route": "rules_lookup",
        "message": "No rule match was found in the rules CSV files.",
    }