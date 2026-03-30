
from __future__ import annotations
# Synonym groups for robust attribute detection

# Deterministic attribute buckets for enriched fields
ENRICHED_FIELD_MAP = [
    (['deductible'], 'deductible', 'Deductible'),
    (['outpatient'], 'outpatient_coverage', 'Outpatient Coverage'),
    (['inpatient', 'ip'], 'inpatient_coverage', 'Inpatient Coverage'),
    (['emergency'], 'emergency_coverage', 'Emergency Coverage'),
    (['pharmacy', 'medicines', 'medication', 'drug'], 'pharmacy_coverage', 'Pharmacy Coverage'),
    (['telemedicine', 'telemed'], 'telemedicine', 'Telemedicine'),
    (['wellness'], 'wellness_benefits', 'Wellness Benefits'),
]

PLAN_FIELD_SYNONYMS = [
    (['annual limit', 'annual maximum', 'maximum limit', 'limit'], 'annual_limit', 'Annual Limit'),
    (['area of coverage', 'coverage area'], 'area_of_coverage', 'Area of Coverage'),
    (['provider network', 'network', 'network provider'], 'provider_network', 'Provider Network'),
    (['copayment', 'copay', 'copayment summary'], 'copayment_summary', 'Copayment'),
    (['reimbursement inside uae', 'uae reimbursement inside', 'reimbursement in uae'], 'reimbursement_inside_uae', 'Reimbursement Inside UAE'),
    (['reimbursement outside uae', 'outside uae reimbursement', 'reimbursement out uae'], 'reimbursement_outside_uae', 'Reimbursement Outside UAE'),
    (['pre-existing conditions', 'pre existing conditions', 'preexisting conditions', 'existing conditions'], 'pre_existing_conditions_note', 'Pre-existing Conditions'),
    (['maternity', 'maternity note', 'maternity benefit'], 'maternity_note', 'Maternity'),
    (['declaration requirements', 'declaration requirement', 'declaration', 'require a declaration', 'declaration needed', 'declaration required'], 'declaration_requirements', 'Declaration Requirements'),
]

import csv

import csv
import re
import unicodedata
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "plans" / "plan_master.csv"

def robust_normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

_normalize = robust_normalize


def _load_rows() -> list[dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plan_name_variants(name: str) -> set:
    """Generate strict variants for plan names (Remedy 04, ريمدي ٠٤, etc.)."""
    variants = set()
    base = _normalize(name)
    variants.add(base)
    # Extract plan number (support both Arabic and English digits)
    import re
    m = re.search(r'(remedy|ريمدي|ريميدي)[\s\-_]*([0-9]+|[٠-٩]+)', base)
    if m:
        prefix = m.group(1)
        num = m.group(2)
        # English and Arabic digit forms
        try:
            num_int = int(num.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')))
            num_en = str(num_int)
            num_en2 = f'{num_int:02d}'
            num_ar = ''.join('٠١٢٣٤٥٦٧٨٩'[int(d)] for d in num_en)
            for p in ["remedy", "ريمدي", "ريميدي"]:
                variants.add(f"{p} {num_en}")
                variants.add(f"{p} {num_en2}")
                variants.add(f"{p} {num_ar}")
        except Exception:
            pass
    return variants

def lookup_plan(query: str) -> dict:

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and re.search(rf'\b{re.escape(variant)}\b', normalized_query):
                # Only allow Remedy 02 (plan_id or plan_name must match Remedy 02)
                allowed_variants = _plan_name_variants("Remedy 02") | _plan_name_variants("REMEDY_02")
                if variant in allowed_variants:
                    matched_row = row
                else:
                    # Block unsupported plans
                    return {"status": "not_found", "answer": "Plan not supported yet"}
                break
        if matched_row:
            break
    if not matched_row:
        return {"status": "not_found"}

    row = matched_row
    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            # Always return the actual value, even if 'Not covered', 'Not included', etc.
            if val is not None:
                return {
                    "status": "found",
                    "route": "plan_lookup",
                    "plan_id": row.get("plan_id"),
                    "matched_plan": row.get("plan_name"),
                    "answer": f"{label} for {row.get('plan_name')} ({row.get('plan_id')}): {val}",
                }

    # 1b. Reimbursement explicit routing
    if "reimbursement" in normalized_query:
        inside = row.get("reimbursement_inside_uae", "")
        outside = row.get("reimbursement_outside_uae", "")
        if inside or outside:
            answer = []
            if inside:
                answer.append(f"Inside UAE: {inside}")
            if outside:
                answer.append(f"Outside UAE: {outside}")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Reimbursement for {row.get('plan_name')} ({row.get('plan_id')}): {' | '.join(answer)}",
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {row.get('plan_name')} ({row.get('plan_id')}): {row.get(col)}",
                    }
    # 3. Fallback: summary
    summary = ", ".join(f"{k}: {v}" for k, v in row.items() if v)
    return {
        "status": "found",
        "route": "plan_lookup",
        "plan_id": row.get("plan_id"),
        "matched_plan": row.get("plan_name"),
        "answer": f"{row.get('plan_name')} ({row.get('plan_id')}): {summary}",
    }

        # (REMOVED DUPLICATE BLOCK)
    return {"status": "not_found"}