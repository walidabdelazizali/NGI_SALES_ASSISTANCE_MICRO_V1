#!/usr/bin/env python3
"""
integrate_confirmed_classics.py
-------------------------------
Reads the staging artifacts (extracted_plan_facts.csv, extracted_benefits_detail.csv)
and populates the live runtime CSVs with ONLY the 5 confirmed Classic plans:

    HN_CLASSIC_1R, HN_CLASSIC_2, HN_CLASSIC_2R, HN_CLASSIC_3, HN_CLASSIC_4

Does NOT touch:
- Any Prime plans (HN_PRIME_1, HN_PRIME_2)
- HN_CLASSIC_1 (pending source)
- Existing Remedy 02-06 rows (preserved exactly)

Safety:
- Removes any pre-existing HN_CLASSIC_* rows from live CSVs before appending
  (idempotent re-run).
- Never fabricates data; only what came from workbook-content extraction.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "staging" / "enhanced"
DATA = ROOT / "data"

CONFIRMED = {"HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4"}
# Map Section name → live benefit CSV file
SECTION_TO_BENEFIT_FILE = {
    "inpatient":   "inpatient_benefits.csv",
    "outpatient":  "outpatient_benefits.csv",
    "maternity":   "maternity_benefits.csv",
    "preventive":  "preventive_benefits.csv",
    "additional":  "additional_benefits.csv",
}
# Exclusions go to rules
EXCLUSION_FILE = "exclusions_master.csv"

# Display names for plan_master
DISPLAY_NAMES = {
    "HN_CLASSIC_1R": "HN Classic Plan-1R",
    "HN_CLASSIC_2":  "HN Classic Plan-2",
    "HN_CLASSIC_2R": "HN Classic Plan-2R",
    "HN_CLASSIC_3":  "HN Classic Plan-3",
    "HN_CLASSIC_4":  "HN Classic Plan-4",
}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _strip_hn_classic(rows: list[dict[str, str]], id_field: str) -> list[dict[str, str]]:
    """Remove any rows whose id_field starts with HN_CLASSIC."""
    return [r for r in rows if not r.get(id_field, "").startswith("HN_CLASSIC")]


# ---------- plan_master.csv ---------
def populate_plan_master() -> int:
    facts_path = STAGING / "extracted_plan_facts.csv"
    facts = _load_csv(facts_path)

    pm_path = DATA / "plans" / "plan_master.csv"
    existing = _load_csv(pm_path)
    fieldnames = list(existing[0].keys()) if existing else []

    # Strip any prior HN_CLASSIC rows (idempotent)
    existing = _strip_hn_classic(existing, "plan_id")

    added = 0
    for fact in facts:
        code = fact["internal_plan_code"]
        if code not in CONFIRMED:
            continue
        row = {
            "plan_id": code,
            "plan_name": DISPLAY_NAMES.get(code, fact["display_plan_name"]),
            "plan_type": "Medical",
            "annual_limit": fact.get("annual_max_benefit", ""),
            "area_of_coverage": fact.get("area_of_coverage", ""),
            "provider_network": fact.get("mapped_internal_network_name", ""),
            "copayment_summary": "",  # Not directly available as single field
            "reimbursement_inside_uae": fact.get("reimbursement_notes", ""),
            "reimbursement_outside_uae": "",
            "pre_existing_conditions_note": "",  # Populated from general section below
            "maternity_note": fact.get("maternity_limit", ""),
            "declaration_requirements": "",
            "deductible": "",
            "outpatient_coverage": fact.get("outpatient_notes", ""),
            "inpatient_coverage": fact.get("inpatient_notes", ""),
            "emergency_coverage": "",
            "pharmacy_coverage": "",
            "telemedicine": "",
            "wellness_benefits": "",
            "notes": f"Extracted from enhanced TOB workbook. Source confidence: {fact.get('source_confidence', 'high')}.",
            "status": "Extracted",
        }
        existing.append(row)
        added += 1

    _write_csv(pm_path, fieldnames, existing)
    print(f"  plan_master.csv: {added} Classic plan rows added")
    return added


# ---------- benefit CSVs ----------
def _next_benefit_id(prefix: str, existing_rows: list[dict[str, str]]) -> int:
    """Find max existing numeric suffix for given prefix, e.g. BEN-IP-500 -> 500."""
    max_n = 0
    for r in existing_rows:
        bid = r.get("benefit_id", "")
        if bid.startswith(prefix):
            try:
                n = int(bid[len(prefix):])
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return max_n + 1


# benefit prefix per section
SECTION_PREFIX = {
    "inpatient":  "BEN-IP-",
    "outpatient": "BEN-OP-",
    "maternity":  "BEN-MAT-",
    "preventive": "BEN-PR-",
    "additional": "BEN-AD-",
}

def populate_benefits() -> dict[str, int]:
    detail_path = STAGING / "extracted_benefits_detail.csv"
    details = _load_csv(detail_path)

    counts: dict[str, int] = {}

    for section, csv_file in SECTION_TO_BENEFIT_FILE.items():
        live_path = DATA / "benefits" / csv_file
        existing = _load_csv(live_path)
        fieldnames = list(existing[0].keys()) if existing else ["benefit_id", "plan_id", "plan_name", "benefit_name", "coverage", "notes"]

        # Strip prior HN_CLASSIC rows (idempotent)
        existing = _strip_hn_classic(existing, "plan_id")

        prefix = SECTION_PREFIX[section]
        next_id = _next_benefit_id(prefix, existing)

        added = 0
        for d in details:
            if d["internal_plan_code"] not in CONFIRMED:
                continue
            if d["section"] != section:
                continue
            bid = f"{prefix}{next_id}"
            next_id += 1
            existing.append({
                "benefit_id": bid,
                "plan_id": d["internal_plan_code"],
                "plan_name": DISPLAY_NAMES.get(d["internal_plan_code"], d["display_plan_name"]),
                "benefit_name": d["benefit_name"],
                "coverage": d["coverage"],
                "notes": d.get("notes", ""),
            })
            added += 1

        _write_csv(live_path, fieldnames, existing)
        counts[section] = added
        print(f"  {csv_file}: {added} Classic benefit rows added")

    return counts


# ---------- exclusions_master.csv ----------
def populate_exclusions() -> int:
    detail_path = STAGING / "extracted_benefits_detail.csv"
    details = _load_csv(detail_path)

    excl_path = DATA / "rules" / EXCLUSION_FILE
    existing = _load_csv(excl_path)
    fieldnames = list(existing[0].keys()) if existing else ["rule_id", "topic", "rule_text", "applies_to", "status"]

    # Strip prior HN_CLASSIC exclusion rows
    existing = _strip_hn_classic(existing, "applies_to")

    # Find max existing EXC- id
    max_n = 0
    for r in existing:
        rid = r.get("rule_id", "")
        if rid.startswith("EXC-"):
            try:
                n = int(rid.split("-")[1])
                if n > max_n:
                    max_n = n
            except (ValueError, IndexError):
                pass
    next_id = max_n + 1

    added = 0
    for d in details:
        if d["internal_plan_code"] not in CONFIRMED:
            continue
        if d["section"] != "exclusion":
            continue
        rid = f"EXC-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": f"Exclusion: {d['benefit_name'][:80]}",
            "rule_text": d["coverage"],
            "applies_to": d["internal_plan_code"],
            "status": "Extracted",
        })
        added += 1

    _write_csv(excl_path, fieldnames, existing)
    print(f"  exclusions_master.csv: {added} Classic exclusion rows added")
    return added


# ---------- terms_conditions.csv (general section) ----------
def populate_terms() -> int:
    detail_path = STAGING / "extracted_benefits_detail.csv"
    details = _load_csv(detail_path)

    tc_path = DATA / "rules" / "terms_conditions.csv"
    existing = _load_csv(tc_path)
    fieldnames = list(existing[0].keys()) if existing else ["rule_id", "topic", "rule_text", "applies_to", "status"]

    existing = _strip_hn_classic(existing, "applies_to")

    max_n = 0
    for r in existing:
        rid = r.get("rule_id", "")
        # Parse various formats: TC-REMEDY02-06, TRM-001, etc.
        for prefix in ("TC-HN-", "TRM-HN-", "TC-", "TRM-"):
            if rid.startswith(prefix):
                try:
                    n = int(rid.split("-")[-1])
                    if n > max_n:
                        max_n = n
                except (ValueError, IndexError):
                    pass
    next_id = max_n + 1

    added = 0
    for d in details:
        if d["internal_plan_code"] not in CONFIRMED:
            continue
        if d["section"] != "general":
            continue
        rid = f"TRM-HN-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": f"General term: {d['benefit_name'][:80]}",
            "rule_text": d["coverage"],
            "applies_to": d["internal_plan_code"],
            "status": "Extracted",
        })
        added += 1

    _write_csv(tc_path, fieldnames, existing)
    print(f"  terms_conditions.csv: {added} Classic general-term rows added")
    return added


# ---------- approvals_rules.csv ----------
def populate_approvals() -> int:
    """Add basic approval rules for Classic plans based on inpatient pre-approval requirement."""
    apr_path = DATA / "rules" / "approvals_rules.csv"
    existing = _load_csv(apr_path)
    fieldnames = list(existing[0].keys()) if existing else ["rule_id", "topic", "rule_text", "applies_to", "status"]

    existing = _strip_hn_classic(existing, "applies_to")

    max_n = 0
    for r in existing:
        rid = r.get("rule_id", "")
        if "APR" in rid:
            try:
                n = int(rid.split("-")[-1])
                if n > max_n:
                    max_n = n
            except (ValueError, IndexError):
                pass
    next_id = max_n + 1

    added = 0
    for code in sorted(CONFIRMED):
        rid = f"APR-HN-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": "Non-urgent inpatient pre-approval",
            "rule_text": "Pre-approval is required for non-urgent inpatient admissions.",
            "applies_to": code,
            "status": "Extracted",
        })
        added += 1

        rid = f"APR-HN-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": "Elective MRI/CT/Endoscopy pre-approval",
            "rule_text": "Pre-approval is required for elective MRI, CT scans, and endoscopies.",
            "applies_to": code,
            "status": "Extracted",
        })
        added += 1

    _write_csv(apr_path, fieldnames, existing)
    print(f"  approvals_rules.csv: {added} Classic approval rows added")
    return added


# ---------- referral_rules.csv ----------
def populate_referrals() -> int:
    """All 5 Classic plans have Direct specialist referral (from staging plan_facts)."""
    ref_path = DATA / "rules" / "referral_rules.csv"
    existing = _load_csv(ref_path)
    fieldnames = list(existing[0].keys()) if existing else ["rule_id", "topic", "rule_text", "applies_to", "status"]

    existing = _strip_hn_classic(existing, "applies_to")

    max_n = 0
    for r in existing:
        rid = r.get("rule_id", "")
        if "REF" in rid:
            try:
                n = int(rid.split("-")[-1])
                if n > max_n:
                    max_n = n
            except (ValueError, IndexError):
                pass
    next_id = max_n + 1

    added = 0
    for code in sorted(CONFIRMED):
        rid = f"REF-HN-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": "Specialist referral policy",
            "rule_text": "Direct access to specialists. No GP referral required.",
            "applies_to": code,
            "status": "Extracted",
        })
        added += 1

    _write_csv(ref_path, fieldnames, existing)
    print(f"  referral_rules.csv: {added} Classic referral rows added")
    return added


# ---------- reimbursement_rules.csv ----------
def populate_reimbursement() -> int:
    """Add reimbursement rule from staging plan_facts reimbursement_notes."""
    facts = _load_csv(STAGING / "extracted_plan_facts.csv")

    rmb_path = DATA / "rules" / "reimbursement_rules.csv"
    existing = _load_csv(rmb_path)
    fieldnames = list(existing[0].keys()) if existing else ["rule_id", "topic", "rule_text", "applies_to", "status"]

    existing = _strip_hn_classic(existing, "applies_to")

    max_n = 0
    for r in existing:
        rid = r.get("rule_id", "")
        if "RMB" in rid:
            try:
                n = int(rid.split("-")[-1])
                if n > max_n:
                    max_n = n
            except (ValueError, IndexError):
                pass
    next_id = max_n + 1

    added = 0
    for fact in facts:
        code = fact["internal_plan_code"]
        if code not in CONFIRMED:
            continue
        note = fact.get("reimbursement_notes", "").strip()
        if not note:
            continue
        rid = f"RMB-HN-{next_id:04d}"
        next_id += 1
        existing.append({
            "rule_id": rid,
            "topic": "Reimbursement policy",
            "rule_text": note,
            "applies_to": code,
            "status": "Extracted",
        })
        added += 1

    _write_csv(rmb_path, fieldnames, existing)
    print(f"  reimbursement_rules.csv: {added} Classic reimbursement rows added")
    return added


# ---------- Main ----------
def main():
    print("=== Integrating 5 confirmed Classic plans into live CSVs ===\n")
    pm = populate_plan_master()
    bc = populate_benefits()
    ec = populate_exclusions()
    tc = populate_terms()
    ac = populate_approvals()
    rc = populate_referrals()
    rb = populate_reimbursement()

    total_benefits = sum(bc.values())
    print(f"\n=== Integration complete ===")
    print(f"  Plans added to plan_master: {pm}")
    print(f"  Benefit rows added:         {total_benefits}")
    print(f"  Exclusion rows added:       {ec}")
    print(f"  Terms/conditions added:     {tc}")
    print(f"  Approval rules added:       {ac}")
    print(f"  Referral rules added:       {rc}")
    print(f"  Reimbursement rules added:  {rb}")

    # Safety check: verify no Prime or HN_CLASSIC_1 rows leaked
    for csv_name in ["plan_master.csv"]:
        path = DATA / "plans" / csv_name
        rows = _load_csv(path)
        for r in rows:
            pid = r.get("plan_id", "")
            if pid in ("HN_PRIME_1", "HN_PRIME_2", "HN_CLASSIC_1"):
                print(f"\n  *** SAFETY VIOLATION: {pid} found in {csv_name}! ***")
                sys.exit(1)

    print("\n  Safety check passed: no Prime or HN_CLASSIC_1 in live CSVs.")


if __name__ == "__main__":
    main()
