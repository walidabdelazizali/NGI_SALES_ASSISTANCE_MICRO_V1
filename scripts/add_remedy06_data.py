"""Add Remedy 06 rows to all CSV files, cloning from R05 with deltas."""
import csv
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def get_fieldnames(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        header = f.readline().strip()
    return header.split(",")


def append_rows(path, rows):
    fieldnames = get_fieldnames(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in rows:
            writer.writerow(row)
    print(f"  Appended {len(rows)} rows to {path}")


def clone_r05(rows, transforms=None):
    cloned = []
    for r in rows:
        nr = dict(r)
        for k, v in nr.items():
            if v is None:
                nr[k] = ""
                continue
            nr[k] = (v
                      .replace("REMEDY_05", "REMEDY_06")
                      .replace("Remedy 05", "Remedy 06")
                      .replace("remedy 05", "remedy 06"))
            if k == "plan_name":
                nr[k] = "NGI Healthnet \u2013 Remedy 06"
        # Benefit IDs: BEN-XX-3YY -> BEN-XX-4YY
        bid = nr.get("benefit_id", "")
        if bid:
            parts = bid.rsplit("-", 1)
            if len(parts) == 2 and parts[1].startswith("3"):
                nr["benefit_id"] = parts[0] + "-4" + parts[1][1:]
        # Rule IDs: XXX-R05-YYY -> XXX-R06-YYY, REMEDY05 -> REMEDY06
        rid = nr.get("rule_id", "")
        if rid:
            nr["rule_id"] = rid.replace("R05", "R06").replace("REMEDY05", "REMEDY06")
        if transforms:
            for field, fn in transforms.items():
                if field in nr:
                    nr[field] = fn(nr[field])
        cloned.append(nr)
    return cloned


def r05_rows(rows):
    return [r for r in rows
            if any("REMEDY_05" in str(v) or "Remedy 05" in str(v)
                   for v in r.values())]


# 1. plan_master
print("=== 1. plan_master.csv ===")
pm = read_csv("data/plans/plan_master.csv")
r05 = [r for r in pm if r.get("plan_id") == "REMEDY_05"]
r06 = clone_r05(r05, transforms={
    "pharmacy_coverage": lambda v: v.replace("7,500", "10,000"),
    "notes": lambda _: ("Curated from Remedy 06 extract. Direct Access to Specialist. "
                         "Direct-access hospitals listed. Reimbursement: general "
                         "reimbursement disallowed UNLESS explicit benefit/rule row "
                         "grants reimbursement."),
})
append_rows("data/plans/plan_master.csv", r06)

# 2. outpatient_benefits
print("=== 2. outpatient_benefits.csv ===")
op = read_csv("data/benefits/outpatient_benefits.csv")
r06_op = clone_r05(r05_rows(op))
for row in r06_op:
    bn = (row.get("benefit_name") or "").lower()
    if "physiotherapy" in bn:
        row["coverage"] = row["coverage"].replace("12 sessions", "20 sessions")
    if "prescribed drugs" in bn or "generic prescribed drugs" in bn:
        row["coverage"] = row["coverage"].replace("7,500", "10,000")
append_rows("data/benefits/outpatient_benefits.csv", r06_op)

# 3. inpatient_benefits
print("=== 3. inpatient_benefits.csv ===")
ip = read_csv("data/benefits/inpatient_benefits.csv")
append_rows("data/benefits/inpatient_benefits.csv", clone_r05(r05_rows(ip)))

# 4. preventive_benefits (+ Shingrix)
print("=== 4. preventive_benefits.csv ===")
pr = read_csv("data/benefits/preventive_benefits.csv")
r06_pr = clone_r05(r05_rows(pr))
r06_pr.append({
    "benefit_id": "BEN-PR-405",
    "plan_id": "REMEDY_06",
    "plan_name": "NGI Healthnet \u2013 Remedy 06",
    "benefit_name": "Shingrix vaccine",
    "coverage": ("Covered for members satisfying DHA eligibility criteria; "
                 "limited to vaccine cost and administration only"),
    "notes": "For Non-LSB Dubai Visa Members only. Curated from Remedy 06 extract.",
})
append_rows("data/benefits/preventive_benefits.csv", r06_pr)

# 5. additional_benefits
print("=== 5. additional_benefits.csv ===")
ad = read_csv("data/benefits/additional_benefits.csv")
append_rows("data/benefits/additional_benefits.csv", clone_r05(r05_rows(ad)))

# 6. maternity_benefits
print("=== 6. maternity_benefits.csv ===")
mt = read_csv("data/benefits/maternity_benefits.csv")
append_rows("data/benefits/maternity_benefits.csv", clone_r05(r05_rows(mt)))

# 7. isa_assist_benefits
print("=== 7. isa_assist_benefits.csv ===")
ia = read_csv("data/benefits/isa_assist_benefits.csv")
append_rows("data/benefits/isa_assist_benefits.csv", clone_r05(r05_rows(ia)))

# 8. terms_conditions
print("=== 8. terms_conditions.csv ===")
tc = read_csv("data/rules/terms_conditions.csv")
append_rows("data/rules/terms_conditions.csv", clone_r05(r05_rows(tc)))

# 9. approvals_rules
print("=== 9. approvals_rules.csv ===")
ar = read_csv("data/rules/approvals_rules.csv")
append_rows("data/rules/approvals_rules.csv", clone_r05(r05_rows(ar)))

# 10. referral_rules
print("=== 10. referral_rules.csv ===")
rr = read_csv("data/rules/referral_rules.csv")
append_rows("data/rules/referral_rules.csv", clone_r05(r05_rows(rr)))

# 11. reimbursement_rules
print("=== 11. reimbursement_rules.csv ===")
rmb = read_csv("data/rules/reimbursement_rules.csv")
append_rows("data/rules/reimbursement_rules.csv", clone_r05(r05_rows(rmb)))

# 12. exclusions_master
print("=== 12. exclusions_master.csv ===")
exc = read_csv("data/rules/exclusions_master.csv")
append_rows("data/rules/exclusions_master.csv", clone_r05(r05_rows(exc)))

# === VERIFICATION ===
print("\n=== VERIFICATION ===")
total = 0
for label, path in [
    ("plan_master", "data/plans/plan_master.csv"),
    ("outpatient", "data/benefits/outpatient_benefits.csv"),
    ("inpatient", "data/benefits/inpatient_benefits.csv"),
    ("preventive", "data/benefits/preventive_benefits.csv"),
    ("additional", "data/benefits/additional_benefits.csv"),
    ("maternity", "data/benefits/maternity_benefits.csv"),
    ("isa_assist", "data/benefits/isa_assist_benefits.csv"),
    ("terms_cond", "data/rules/terms_conditions.csv"),
    ("approvals", "data/rules/approvals_rules.csv"),
    ("referral", "data/rules/referral_rules.csv"),
    ("reimburse", "data/rules/reimbursement_rules.csv"),
    ("exclusions", "data/rules/exclusions_master.csv"),
]:
    rows = read_csv(path)
    r06 = [r for r in rows if any("REMEDY_06" in str(v) for v in r.values())]
    total += len(r06)
    print(f"  {label}: {len(r06)} R06 rows")
print(f"\nTOTAL R06 rows: {total}")

# Delta checks
print("\n=== DELTA VERIFICATION ===")
op_rows = read_csv("data/benefits/outpatient_benefits.csv")
for r in op_rows:
    if r.get("plan_id") == "REMEDY_06":
        bn = (r.get("benefit_name") or "").lower()
        if "physiotherapy" in bn:
            assert "20 sessions" in r["coverage"], f"FAIL physio: {r['coverage']}"
            print(f"  Physio OK: {r['coverage'][:70]}")
        if bn == "prescribed drugs":
            assert "10,000" in r["coverage"], f"FAIL drugs: {r['coverage']}"
            print(f"  Drugs OK: {r['coverage'][:70]}")
        if bn == "generic prescribed drugs":
            assert "10,000" in r["coverage"], f"FAIL generic: {r['coverage']}"
            print(f"  Generic drugs OK: {r['coverage'][:70]}")

pr_rows = read_csv("data/benefits/preventive_benefits.csv")
r06_prev = [r for r in pr_rows if r.get("plan_id") == "REMEDY_06"]
shingrix = any("shingrix" in (r.get("benefit_name") or "").lower() for r in r06_prev)
print(f"  Shingrix present: {shingrix}")
print(f"  Preventive count: {len(r06_prev)} (expect 5)")

pm_rows = read_csv("data/plans/plan_master.csv")
for r in pm_rows:
    if r.get("plan_id") == "REMEDY_06":
        assert "10,000" in (r.get("pharmacy_coverage") or ""), "Pharmacy not 10k"
        print(f"  Plan pharmacy: {r['pharmacy_coverage'][:70]}")

print("\nDone!")
