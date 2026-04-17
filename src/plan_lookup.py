from __future__ import annotations
# Synonym groups for robust attribute detection

# Deterministic attribute buckets for enriched fields
ENRICHED_FIELD_MAP = [
    (['deductible', 'خصم', 'ديكتبل', 'ديدكتبل'], 'deductible', 'Deductible'),
    (['outpatient', 'عيادات خارجية', 'خارجي'], 'outpatient_coverage', 'Outpatient Coverage'),
    (['inpatient', 'ip', 'تنويم', 'داخلي', 'عيادات داخلية'], 'inpatient_coverage', 'Inpatient Coverage'),
    (['emergency', 'طوارئ', 'الطوارئ'], 'emergency_coverage', 'Emergency Coverage'),
    (['pharmacy', 'medicines', 'medication', 'drug', 'صيدلية', 'أدوية', 'دواء'], 'pharmacy_coverage', 'Pharmacy Coverage'),
    (['telemedicine', 'telemed', 'online consultation', 'online doctor', 'video consultation', 'remote consultation', 'doctor online', 'تلي ميديسن', 'التلي ميديسن', 'طب عن بعد', 'تيليمديسن', 'تيليمديسين', 'استشارة عن بعد', 'استشاره عن بعد'], 'telemedicine', 'Telemedicine'),
    (['wellness', 'عافية', 'العافية', 'ويلنس'], 'wellness_benefits', 'Wellness Benefits'),
]

PLAN_FIELD_SYNONYMS = [
    (['annual limit', 'annual maximum', 'maximum limit', 'limit', 'الحد السنوي', 'الحد الاقصى السنوي', 'السقف السنوي', 'حد سنوي', 'الحد الأقصى', 'كم الحد', 'شو الحد', 'الليمت', 'ليمت', 'انيوال ليمت'], 'annual_limit', 'Annual Limit'),
    (['area of coverage', 'coverage area', 'منطقة التغطية', 'نطاق التغطية', 'التغطية الجغرافية', 'وين التغطية', 'اين التغطية', 'منطقه التغطيه', 'التغطية', 'تغطية'], 'area_of_coverage', 'Area of Coverage'),
    (['provider network', 'network', 'network provider', 'شبكة المستشفيات', 'شبكة العلاج', 'الشبكة الطبية'], 'provider_network', 'Provider Network'),
    (['copayment', 'copay', 'copayment summary', 'كوبي', 'الكوبي', 'كوباي', 'الكوباي', 'نسبة التحمل', 'تحمل المريض', 'نسبة المشاركة', 'حصة المريض'], 'copayment_summary', 'Copayment'),
    (['reimbursement inside uae', 'uae reimbursement inside', 'reimbursement in uae', 'استرداد داخل الامارات', 'تعويض داخل'], 'reimbursement_inside_uae', 'Reimbursement Inside UAE'),
    (['reimbursement outside uae', 'outside uae reimbursement', 'reimbursement out uae', 'استرداد خارج الامارات', 'تعويض خارج'], 'reimbursement_outside_uae', 'Reimbursement Outside UAE'),
    (['pre-existing conditions', 'pre existing conditions', 'preexisting conditions', 'existing conditions', 'حالات مزمنة', 'حالة مزمنة', 'امراض سابقة', 'حالة سابقة', 'حالات سابقه'], 'pre_existing_conditions_note', 'Pre-existing Conditions'),
    (['maternity', 'maternity note', 'maternity benefit', 'حمل', 'ولادة', 'ولاده', 'ماتيرنيتي', 'تغطية الحمل', 'تغطية حمل', 'تغطية الولادة', 'الأمومة', 'أمومة', 'الامومة', 'امومة'], 'maternity_note', 'Maternity'),
    (['declaration requirements', 'declaration requirement', 'declaration', 'require a declaration', 'declaration needed', 'declaration required', 'اقرار', 'الاقرار', 'متطلبات الاقرار'], 'declaration_requirements', 'Declaration Requirements'),
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
    # Strip Arabic punctuation (؟،؛) before the main cleanup
    text = re.sub(r'[\u060C\u061B\u061F\u0640]', ' ', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

_normalize = robust_normalize


def _load_rows() -> list[dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plan_name_variants(name: str) -> set:
    """Generate strict variants for plan names (Remedy 02-06, HN Classic 1R-4)."""
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
    # Classic plan variants: match "classic 1r", "hn_classic_1r", "hn classic plan 1r", "كلاسيك 2", etc.
    cm = re.search(r'(?:hn[\s_]?)?(?:classic|\u0643\u0644\u0627\u0633\u064a\u0643)[\s_]*(?:plan[\s_]*)?(1r|2r|1|2|3|4)\b', base)
    if cm:
        suffix = cm.group(1)
        for p in ["classic", "hn classic", "hn_classic", "\u0643\u0644\u0627\u0633\u064a\u0643"]:
            variants.add(f"{p} {suffix}")
            variants.add(f"{p} plan {suffix}")
            variants.add(f"{p}_{suffix}")
        variants.add(f"hn_classic_{suffix}")
    return variants

# Import canonical plan sets from centralized alias policy
from plan_alias_policy import CONFIRMED_CLASSIC_IDS, CONFIRMED_REMEDY_IDS, DEPLOYMENT_APPROVED_PLANS

def _all_allowed_variants() -> set:
    """Return the full set of allowed plan name variants (Remedy + Classic)."""
    s = set()
    for r in ("Remedy 02", "REMEDY_02", "Remedy 03", "REMEDY_03",
              "Remedy 04", "REMEDY_04", "Remedy 05", "REMEDY_05",
              "Remedy 06", "REMEDY_06"):
        s |= _plan_name_variants(r)
    for c in CONFIRMED_CLASSIC_IDS:
        s |= _plan_name_variants(c)
    return s

def lookup_plan(query: str) -> dict:
    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None

    # PLAN GATE: Remedy 02-06 and confirmed Classic plans are supported.
    import re
    plan_regex = r"remedy[\s\-_]?(\d{2,})"
    plan_match = re.search(plan_regex, query.lower())
    if plan_match and plan_match.group(1) not in ["02", "03", "04", "05", "06"]:
        # Explicit unsupported Remedy plan: block any fallback
        return {"status": "not_found", "answer": "Plan not supported yet"}

    # Deployment scope: confirmed but not-yet-approved plans return safe fallback
    if plan_match:
        _candidate = f"REMEDY_{plan_match.group(1)}"
        if _candidate not in DEPLOYMENT_APPROVED_PLANS:
            return {"status": "not_found"}

    # Classic plan gate: check if the query mentions a Classic plan
    classic_regex = r"(?:hn[_\s]?)?(?:classic|\u0643\u0644\u0627\u0633\u064a\u0643)[_\s]*(?:plan[_\s]*)?(1r|2r|2|3|4|1)\b"
    classic_match = re.search(classic_regex, query.lower())
    if classic_match:
        classic_suffix = classic_match.group(1).upper()
        classic_code = f"HN_CLASSIC_{classic_suffix}"
        if classic_code not in CONFIRMED_CLASSIC_IDS:
            return {"status": "not_found", "answer": "Plan not supported yet"}
        if classic_code not in DEPLOYMENT_APPROVED_PLANS:
            return {"status": "not_found"}


    # --- PATCH: prioritize explicit 'remedy 03' and 'remedy 02' plan id matching ---
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        allowed_variants = _all_allowed_variants()
        # If the query contains an allowed variant (e.g., 'remedy 03', 'ريمدي 02'), match the corresponding row
        for allowed in allowed_variants:
            if allowed in normalized_query:
                # Only match the correct plan row — use plan_variants to handle Arabic names
                if allowed in plan_variants:
                    matched_row = row
                    break
        if matched_row:
            break
    if not matched_row:
        # Fallback to old logic if needed (should not trigger for explicit queries)
        for row in rows:
            plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
            for variant in plan_variants:
                if variant and variant in normalized_query:
                    if variant in allowed_variants:
                        matched_row = row
                    else:
                        return {"status": "not_found", "answer": "Plan not supported yet"}
                    break
            if matched_row:
                break
    if not matched_row:
        return {"status": "not_found"}


    row = matched_row
    # MINI PATCH: explicit benefit/rule/intent/alias mapping for Remedy 02 and 03
    # 1. Explicit benefit mapping
    benefit_map = [
        (['physiotherapy', 'علاج طبيعي', 'العلاج الطبيعي'], 'Physiotherapy', 'outpatient_benefits', 'Physiotherapy'),
        (['dental', 'أسنان', 'تغطية أسنان', 'الاسنان', 'الأسنان'], 'Dental', 'additional_benefits', 'dental'),
        (['mri', 'magnetic resonance', 'تصوير بالرنين', 'الرنين المغناطيسي', 'رنين مغناطيسي'], 'MRI', 'outpatient_benefits', 'MRI'),
        (['ct scan', 'computed tomography', 'سي تي', 'تصوير مقطعي'], 'CT scan', 'outpatient_benefits', 'CT scan'),
        (['endoscopy', 'منظار', 'تنظير'], 'Endoscopy', 'outpatient_benefits', 'Endoscopy'),
        (['laboratory', 'lab test', 'تحاليل', 'اختبار معملي'], 'Laboratory tests', 'outpatient_benefits', 'Laboratory tests carried out in authorized facility'),
        (['radiology', 'تشخيص بالأشعة', 'تصوير شعاعي'], 'Radiology', 'outpatient_benefits', 'Radiology diagnostic services carried out in authorized facility'),
        (['prescribed drugs', 'generic prescribed drugs', 'generic drugs', 'أدوية جنيسة', 'أدوية موصوفة', 'medicines', 'أدوية'], 'Prescribed drugs', 'outpatient_benefits', 'Prescribed drugs'),
        (['optical', 'نظارات', 'بصريات'], 'Optical', 'additional_benefits', 'Optical benefits'),  # Optical = discount-only (25%), not insured coverage
        (['optical', 'vision', 'نظارات', 'بصريات', 'بصر'], 'Vision/Optical', 'additional_benefits', 'vision'),  # Fallback for enhanced plans
        (['doctor consultation', 'doctor visit', 'consultation fee', 'استشارة طبيب', 'زيارة طبيب', 'general practitioner'], 'Doctor consultation', 'outpatient_benefits', 'Examination, diagnostic and treatment by authorized general practitioners'),
        (['diagnostics', 'diagnostic test', 'فحوصات'], 'Diagnostics', 'outpatient_benefits', 'Laboratory tests carried out'),
        (['shingrix', 'shingrix vaccine', 'شينجريكس'], 'Shingrix vaccine', 'preventive_benefits', 'Shingrix vaccine'),  # R06 only; R02-R05 have no Shingrix row
        (['influenza', 'influenza vaccine', 'flu vaccine', 'flu shot', 'لقاح الانفلونزا', 'تطعيم الانفلونزا'], 'Influenza vaccine', 'preventive_benefits', 'Influenza vaccine'),
        (['pneumococcal', 'pneumococcal vaccine', 'لقاح المكورات'], 'Pneumococcal vaccine', 'preventive_benefits', 'pneumococcal conjugate vaccine'),
        (['vaccine', 'vaccination', 'immunization', 'تطعيم', 'لقاح', 'تطعيمات'], 'Preventive vaccines', 'preventive_benefits', 'Preventive services vaccines and immunizations'),
    ]
    import csv
    for terms, label, benefit_file, benefit_name in benefit_map:
        explicit_plan = None
        if any(term in normalized_query for term in terms):
            if label in ('Physiotherapy', 'Prescribed drugs'):
                if (explicit_plan is None and (
                    'remedy 03' in normalized_query or 'ريمدي 03' in normalized_query or 'remedy_03' in normalized_query)):
                    explicit_plan = 'REMEDY_03'
            benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / f'{benefit_file}.csv'
            with open(benefit_path, encoding='utf-8', newline='') as f:
                reader = list(csv.DictReader(f))
                explicit_plan = None
                # PLAN DETECTION for benefit lookup: highest plan checked first to avoid shadowing.
                # R05/R06 have Direct Access to Specialist (no GP referral).
                if 'remedy 06' in normalized_query or 'ريمدي 06' in normalized_query or 'remedy_06' in normalized_query:
                    explicit_plan = 'REMEDY_06'
                elif 'remedy 05' in normalized_query or 'ريمدي 05' in normalized_query or 'remedy_05' in normalized_query:
                    explicit_plan = 'REMEDY_05'
                elif 'remedy 04' in normalized_query or 'ريمدي 04' in normalized_query or 'remedy_04' in normalized_query:
                    explicit_plan = 'REMEDY_04'
                elif 'remedy 02' in normalized_query or 'ريمدي 02' in normalized_query or 'remedy_02' in normalized_query:
                    explicit_plan = 'REMEDY_02'
                elif 'remedy 03' in normalized_query or 'ريمدي 03' in normalized_query or 'remedy_03' in normalized_query:
                    explicit_plan = 'REMEDY_03'
                # Classic plan detection
                if not explicit_plan:
                    import re as _re
                    _cm = _re.search(r'(?:hn[_\s]?)?classic[_\s]*(?:plan[_\s]*)?(1r|2r|1|2|3|4)\b', normalized_query)
                    if _cm:
                        _cc = f"HN_CLASSIC_{_cm.group(1).upper()}"
                        if _cc in CONFIRMED_CLASSIC_IDS:
                            explicit_plan = _cc
                if not explicit_plan and matched_row:
                    explicit_plan = matched_row.get('plan_id')
                found = False
                for brow in reader:
                    if (
                        brow.get('plan_id', '') == 'plan_id' or
                        brow.get('benefit_name', '') == 'benefit_name' or
                        not brow.get('plan_id') or not brow.get('benefit_name')
                    ):
                        continue
                    if explicit_plan and brow['plan_id'] != explicit_plan:
                        continue
                    if benefit_name.lower() in brow['benefit_name'].lower():
                        # For prescribed drugs, require name starts with 'prescribed drugs'
                        if label == 'Prescribed drugs' and not brow['benefit_name'].strip().lower().startswith('prescribed drugs'):
                            continue
                        # For MRI/CT scan, append pre-approval note
                        _notes = brow.get('notes', '').strip()
                        _notes_suffix = '' if _notes == brow['coverage'].strip() else f' {_notes}'
                        if label in ['MRI', 'CT scan']:
                            return {
                                "status": "found",
                                "route": "plan_lookup",
                                "plan_id": brow.get("plan_id"),
                                "matched_plan": brow.get("plan_name"),
                                "answer": f"{label} for {brow.get('plan_name')}: {brow['coverage']}. Elective {label} requires pre-approval.{_notes_suffix}"
                            }
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": brow.get("plan_id"),
                            "matched_plan": brow.get("plan_name"),
                            "answer": f"{label} for {brow.get('plan_name')}: {brow['coverage']}.{_notes_suffix}"
                        }
                        found = True
                # Dental fallback: if not found and explicit_plan is supported, search broadly for any dental row
                if label == 'Dental' and explicit_plan and not found:
                    for brow in reader:
                        if (
                            brow.get('plan_id', '') == 'plan_id' or
                            brow.get('benefit_name', '') == 'benefit_name' or
                            not brow.get('plan_id') or not brow.get('benefit_name')
                        ):
                            continue
                        if brow['plan_id'] == explicit_plan and 'dental' in brow['benefit_name'].lower():
                            return {
                                "status": "found",
                                "route": "plan_lookup",
                                "plan_id": brow.get("plan_id"),
                                "matched_plan": brow.get("plan_name"),
                                "answer": f"Dental for {brow.get('plan_name')}: {brow['coverage']}. {brow.get('notes','').strip()}"
                            }
                    plan_label = explicit_plan.replace('REMEDY_', 'Remedy ').replace('HN_CLASSIC_', 'Classic Plan-')
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": explicit_plan,
                        "matched_plan": plan_label,
                        "answer": f"Dental is not confirmed as a covered benefit under {plan_label}."
                    }
                # Hotfix: "Not listed" fallback for preventive benefits when plan is valid but specific benefit missing
                if benefit_file == 'preventive_benefits' and explicit_plan and not found:
                    plan_short = explicit_plan.replace('REMEDY_', 'Remedy ')
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": explicit_plan,
                        "answer": f"{label} is not listed under {plan_short}."
                    }
        # --- PATCH: Non-urgent inpatient approval for Remedy 03 ---
        if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
            if matched_row and matched_row.get('plan_id') == 'REMEDY_04':
                return {
                    "status": "found",
                    "route": "plan_lookup",
                    "plan_id": "REMEDY_04",
                    "matched_plan": "NGI Healthnet – Remedy 04",
                    "answer": "Non-urgent inpatient treatment for Remedy 04: Pre-approval required. 20% copay applies, with AED 500 per incident cap and AED 1,000 per year cap."
                }
            if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
                # Explicit Remedy 03 answer (no fallback)
                return {
                    "status": "found",
                    "route": "plan_lookup",
                    "plan_id": "REMEDY_03",
                    "matched_plan": "NGI Healthnet – Remedy 03",
                    "answer": "Non-urgent inpatient treatment for Remedy 03: Pre-approval required. 20% copay applies, with AED 500 per incident cap and AED 1,000 per year cap."
                }
            # Fallback to Remedy 02 (existing logic)
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": "REMEDY_02",
                "matched_plan": "REMEDY 02",
                "answer": "Non-urgent inpatient treatment for Remedy 02: Pre-approval required. 20% copay applies, with AED 500 per incident cap and AED 1,000 per year cap."
            }
    # 2. Maternity intent split
    if 'waiting period' in normalized_query or 'فترة الانتظار' in normalized_query:
        # BUG FIX (stabilized): filter by target_plan so the requested plan's row wins.
        # Without this, the first CSV row (often R03) was returned regardless of query.
        target_plan = matched_row.get('plan_id') if matched_row else None
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if (brow['plan_id'].startswith('REMEDY_') or brow['plan_id'] in CONFIRMED_CLASSIC_IDS) and 'waiting period' in brow['benefit_name'].lower():
                    if target_plan and brow['plan_id'] != target_plan:
                        continue
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Maternity waiting period for {brow.get('plan_name')}: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        # Prenatal handler — filter by target_plan so the requested plan's row wins (same pattern as WP fix).
        target_plan = matched_row.get('plan_id') if matched_row else None
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if not (brow['plan_id'].startswith('REMEDY_') or brow['plan_id'] in CONFIRMED_CLASSIC_IDS):
                    continue
                if 'prenatal' not in brow['benefit_name'].lower():
                    continue
                if target_plan and brow['plan_id'] != target_plan:
                    continue
                return {
                    "status": "found",
                    "route": "plan_lookup",
                    "plan_id": brow.get("plan_id"),
                    "matched_plan": brow.get("plan_name"),
                    "answer": f"Prenatal services for {brow.get('plan_name')}: {brow['coverage']}. {brow.get('notes','').strip()}"
                }
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        # Newborn handler — filter by target_plan so the requested plan's row wins (same pattern as WP fix).
        target_plan = matched_row.get('plan_id') if matched_row else None
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if not (brow['plan_id'].startswith('REMEDY_') or brow['plan_id'] in CONFIRMED_CLASSIC_IDS):
                    continue
                if 'newborn' not in brow['benefit_name'].lower():
                    continue
                if target_plan and brow['plan_id'] != target_plan:
                    continue
                return {
                    "status": "found",
                    "route": "plan_lookup",
                    "plan_id": brow.get("plan_id"),
                    "matched_plan": brow.get("plan_name"),
                    "answer": f"Newborn cover for {brow.get('plan_name')}: {brow['coverage']}. {brow.get('notes','').strip()}"
                }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and (
                        'room and board' in arow.get('topic','').lower() or 'non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
            # If not found, do not fallback to Remedy 02
            return {"status": "not_found", "answer": "No Remedy 03 non-urgent inpatient approval rule found."}
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # 2a. Generic "benefits" / "فوائد" / "المزايا" overview handler
    _generic_benefit_terms = ['فوائد', 'فوايد', 'المزايا', 'مزايا', 'benefits', 'what does it cover', 'شو يغطي', 'شو فيها']
    if any(_normalize(t) in normalized_query for t in _generic_benefit_terms):
        plan_short = row.get("plan_name") or row.get("plan_id", "")
        _overview_parts = []
        _annual = row.get("annual_limit")
        _area = row.get("area_of_coverage")
        _copay = row.get("copayment_summary")
        _network = row.get("provider_network")
        _maternity = row.get("maternity_note")
        _reimburse_in = row.get("reimbursement_inside_uae")
        if _annual:
            _overview_parts.append(f"Annual Limit: {_annual}")
        if _area:
            _overview_parts.append(f"Area of Coverage: {_area}")
        if _copay:
            _overview_parts.append(f"Copayment: {_copay}")
        if _network:
            _overview_parts.append(f"Provider Network: {_network}")
        if _maternity:
            _overview_parts.append(f"Maternity: {_maternity}")
        if _reimburse_in:
            _overview_parts.append(f"Reimbursement (inside UAE): {_reimburse_in}")
        if _overview_parts:
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"{plan_short} — Overview:\n" + "\n".join(f"• {p}" for p in _overview_parts),
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
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
    # 0. Robust Arabic/English maternity intent detection
    maternity_phrases = [
        'حمل', 'maternity', 'فيها حمل', 'تشمل حمل', 'هل فيها ولادة', 'ولادة', 'ماتيرنيتي', 'maternity benefit', 'maternity note', 'maternity coverage'
    ]
    if any(phrase in normalized_query for phrase in maternity_phrases):
        val = row.get('maternity_note')
        if val:
            plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
            return {
                "status": "found",
                "route": "plan_lookup",
                "plan_id": row.get("plan_id"),
                "matched_plan": row.get("plan_name"),
                "answer": f"Maternity for {plan_short}: {val}."
            }

    # 1. Deterministic enriched field detection (improved for failing fields)
    for keywords, col, label in ENRICHED_FIELD_MAP:
        if any(kw in normalized_query for kw in keywords):
            val = row.get(col)
            if val is not None:
                # Owner-friendly phrasing
                plan_short = row.get("plan_id", "REMEDY_02").replace("REMEDY_", "Remedy ")
                if col == "deductible":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Deductible for {plan_short}: {val}."
                    }
                elif col == "telemedicine":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Telemedicine in {plan_short}: {val}."
                    }
                elif col == "wellness_benefits":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Wellness benefits in {plan_short}: {val}."
                    }
                elif col == "outpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Outpatient coverage for {plan_short}: {val}."
                    }
                elif col == "inpatient_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Inpatient coverage for {plan_short}: {val}."
                    }
                elif col == "emergency_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Emergency coverage for {plan_short}: {val}."
                    }
                elif col == "pharmacy_coverage":
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"Pharmacy coverage for {plan_short}: {val}."
                    }
                else:
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": row.get("plan_id"),
                        "matched_plan": row.get("plan_name"),
                        "answer": f"{label} for {plan_short}: {val}."
                    }

    # 1b. Reimbursement explicit routing
    if any(t in normalized_query for t in ["reimbursement", "استرداد", "تعويض", "استرجاع"]):
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
                "answer": f"Reimbursement for {row.get("plan_name") or row.get("plan_id", "")}: {' | '.join(answer)}."
            }

    # 2. Classic fields (non-enriched)
    for synonyms, col, label in PLAN_FIELD_SYNONYMS:
        for syn in synonyms:
            syn_tokens = set(_normalize(syn).split())
            if syn_tokens and syn_tokens.issubset(query_tokens):
                if col in row and row.get(col):
                    plan_short = row.get("plan_name") or row.get("plan_id")
                    if col == "annual_limit":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Annual limit for {plan_short}: {row.get(col)}."
                        }
                    elif col == "area_of_coverage":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Area of Coverage for {plan_short}: {row.get(col)}."
                        }
                    elif col == "provider_network":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Provider Network for {plan_short}: {row.get(col)}."
                        }
                    elif col == "copayment_summary":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Copayment for {plan_short}: {row.get(col)}."
                        }
                    elif col == "pre_existing_conditions_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Pre-existing Conditions for {plan_short}: {row.get(col)}."
                        }
                    elif col == "maternity_note":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Maternity for {plan_short}: {row.get(col)}."
                        }
                    elif col == "declaration_requirements":
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"Declaration Requirements for {plan_short}: {row.get(col)}."
                        }
                    else:
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": row.get("plan_id"),
                            "matched_plan": row.get("plan_name"),
                            "answer": f"{label} for {plan_short}: {row.get(col)}."
                        }
    # --- PATCH: Remedy 03 pre-existing condition rules specialization ---
    if any(term in normalized_query for term in ['pre-existing', 'pre existing', 'preexisting', 'chronic', 'undeclared']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Pre-existing and chronic conditions for Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            rules_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'terms_conditions.csv'
            with open(rules_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'pre-existing' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Pre-existing and chronic conditions for Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 GP referral for specialist consultation ---
    if any(term in normalized_query for term in ['gp referral', 'specialist consultation', 'specialist referral', 'see a specialist', 'consultant', 'استشاري', 'إحالة', 'إحالة طبيب عام']):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_03' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"GP referral for specialist consultation in Remedy 03: {rrow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            referral_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'referral_rules.csv'
            with open(referral_path, encoding='utf-8', newline='') as rf:
                rreader = csv.DictReader(rf)
                for rrow in rreader:
                    if rrow.get('applies_to') == 'REMEDY_02' and 'specialist' in rrow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"GP referral for specialist consultation in Remedy 02: {rrow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 non-urgent inpatient approval ---
    if ('non-urgent inpatient' in normalized_query or 'non urgent inpatient' in normalized_query or 'غير طارئة' in normalized_query):
        if matched_row and matched_row.get('plan_id') == 'REMEDY_03':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_03' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_03",
                            "matched_plan": "NGI Healthnet – Remedy 03",
                            "answer": f"Non-urgent inpatient treatment for Remedy 03: {arow['rule_text']}"
                        }
        elif matched_row and matched_row.get('plan_id') == 'REMEDY_02':
            approval_path = Path(__file__).resolve().parents[1] / 'data' / 'rules' / 'approvals_rules.csv'
            with open(approval_path, encoding='utf-8', newline='') as af:
                areader = csv.DictReader(af)
                for arow in areader:
                    if arow.get('applies_to') == 'REMEDY_02' and 'room and board' in arow.get('topic','').lower():
                        return {
                            "status": "found",
                            "route": "plan_lookup",
                            "plan_id": "REMEDY_02",
                            "matched_plan": "REMEDY 02",
                            "answer": f"Non-urgent inpatient treatment for Remedy 02: {arow['rule_text']}"
                        }

    # --- PATCH: Remedy 03 prenatal services ---
    if any(term in normalized_query for term in ['prenatal', 'pre-natal', 'antenatal', 'ما قبل الولادة']):
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'prenatal' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Prenatal services for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    # --- PATCH: Remedy 03 newborn cover ---
    if 'newborn' in normalized_query or 'حديثي الولادة' in normalized_query:
        benefit_path = Path(__file__).resolve().parents[1] / 'data' / 'benefits' / 'maternity_benefits.csv'
        with open(benefit_path, encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for brow in reader:
                if matched_row and matched_row.get('plan_id') == 'REMEDY_03' and brow['plan_id'] == 'REMEDY_03' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 03: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }
                elif matched_row and matched_row.get('plan_id') == 'REMEDY_02' and brow['plan_id'] == 'REMEDY_02' and 'newborn' in brow['benefit_name'].lower():
                    return {
                        "status": "found",
                        "route": "plan_lookup",
                        "plan_id": brow.get("plan_id"),
                        "matched_plan": brow.get("plan_name"),
                        "answer": f"Newborn cover for Remedy 02: {brow['coverage']}. {brow.get('notes','').strip()}"
                    }

    normalized_query = _normalize(query)
    rows = _load_rows()
    query_tokens = set(normalized_query.split())
    matched_row = None
    for row in rows:
        plan_variants = _plan_name_variants(row.get("plan_name", "")) | _plan_name_variants(row.get("plan_id", ""))
        for variant in plan_variants:
            if variant and variant in normalized_query:
                # Allow Remedy 02, Remedy 03, and Remedy 04
                allowed_variants = _all_allowed_variants()
                if variant in allowed_variants:
                    matched_row = row
                else:
                    return {"status": "not_found", "answer": "Plan not supported yet"}
                break
        if matched_row:
            break

    return {"status": "not_found"}
