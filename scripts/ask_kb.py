import sys
from pathlib import Path

import re
import unicodedata

# Ensure src is in sys.path for import
SRC_DIR = Path(__file__).resolve().parent.parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from training_qa_lookup import lookup_training_qa
from plan_lookup import lookup_plan
from network_lookup import lookup_network
from plan_alias_policy import resolve_plan_alias, CONFIRMED_CLASSIC_IDS, CONFIRMED_REMEDY_IDS, DEPLOYMENT_APPROVED_PLANS

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
TRAINING_QA_CSV = DATA_DIR / 'training_questions_master.csv'


# Robust normalization for Arabic/English/mixed queries
def robust_normalize(text):
    if not isinstance(text, str):
        return ""
    # Convert Arabic digits to English
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    # Remove diacritics and normalize unicode
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    # Lowercase and strip
    text = text.lower().strip()
    # Remove non-alphanumeric (keep Arabic letters)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text

def clean_output(text):
    """Remove internal/non-client-facing notes and normalise formatting.

    Phase Q1 additions: plan-name unification, Classic maternity restructure,
    label normalisation, reimbursement separator, and AED/currency fixes.
    """
    if not isinstance(text, str):
        return text

    # ── 1. Strip internal curation / classification notes ──
    text = re.sub(r'\s*Curated from Remedy \d{2,} extract\.?', '', text)
    text = re.sub(r'\s*Treated as [^.]+\bfor coverage\.?', '', text)

    # ── 2. Currency fixes ──
    # "AED 3. 000" → "AED 3,000"
    text = re.sub(r'AED\s+(\d{1,3})\.\s(\d{3})', r'AED \1,\2', text)
    # Dot-stuck: "AED.12,500" / "AED. 12,500" → "AED 12,500"
    text = re.sub(r'AED\.\s*(\d)', r'AED \1', text)
    # Remove "/-" suffix after AED amounts (with optional whitespace)
    text = re.sub(r'(AED\s[\d,]+)\s*/\-', r'\1', text)
    # Add commas to bare AED amounts (AED 150000 → AED 150,000)
    def _fmt_aed(m):
        return 'AED ' + f'{int(m.group(1)):,}'
    text = re.sub(r'AED\s+(\d{4,})', _fmt_aed, text)

    # ── 3. Plan-name normalisation ──
    text = re.sub(r'NGI Healthnet\s*[\u2013\u2014\u2013\u2014–—-]\s*Remedy\s*(\d{2})', r'Remedy \1', text)
    text = re.sub(r'REMEDY\s+(\d{2})', r'Remedy \1', text)
    # Classic plan IDs → client-facing: HN_CLASSIC_2 / HN Classic Plan-2 → Classic Plan-2
    text = re.sub(r'\bHN[_\s](?:CLASSIC|Classic)[_\s]?(?:Plan[_\s\-]?)?(\w+)', r'Classic Plan-\1', text)

    # ── 4. Unit formatting ──
    text = re.sub(r'(\d+)\s+percent\b', r'\1%', text)

    # ── 5. Maternity label dedup ──
    # "Maternity for <plan>: Maternity covered …" → "Maternity for <plan>: Covered …"
    text = re.sub(r'(Maternity for [^:]+:\s*)Maternity covered', r'\1Covered', text, flags=re.IGNORECASE)

    # ── 6. Classic maternity — restructure raw source text ──
    _mat = re.search(
        r'Covered with\s+(\S+)\s+co-insurance\s+up\s+payable\s+by\s+the\s+insured\)\s*'
        r'Normal Delivery:\s*Aggregate Limit Per Year:\s*AED\s*([\d,]+)\s*'
        r'Medically necessary Cesarean Section,?\s*Complications\s*&\s*Medically Necessary Termination:\s*'
        r'Aggregate Limit Per Year:\s*AED\s*([\d,]+)'
        r'(?:\s*(?:/\-)?\s*\(Where any condition develops which becomes life threatening to either the mother or the new born,?\s*'
        r'the medically necessary expenses will be covered up to AED\s*([\d,]+)\s*(?:/\-)?\s*\))?',
        text, re.IGNORECASE,
    )
    if _mat:
        _coins = _mat.group(1).lower()
        _coins_lbl = 'nil co-insurance' if _coins == 'nil' else f'{_coins} co-insurance'
        _parts = [
            f'Covered ({_coins_lbl}).',
            f'Normal delivery: up to AED {_mat.group(2)}/year.',
            f'Cesarean/complications: up to AED {_mat.group(3)}/year.',
        ]
        if _mat.group(4):
            _parts.append(f'Life-threatening conditions: up to AED {_mat.group(4)}.')
        text = text[:_mat.start()] + ' '.join(_parts) + text[_mat.end():]

    # ── 7. Reimbursement: pipe separator → period ──
    text = re.sub(r'(Inside UAE:.*?)\s*\|\s*(Outside UAE:)', r'\1. \2', text)

    # ── 8. Label normalisation ──
    text = re.sub(r'Pharmacy coverage for\b', 'Pharmacy for', text)

    # ── 9. Final whitespace / period cleanup ──
    text = re.sub(r'\s{2,}', ' ', text).strip()
    text = re.sub(r'\.\s*\.', '.', text)
    return text

PLAN_ATTRS = [
    'annual limit', 'annual_max', 'limit', 'area of coverage', 'coverage', 'network', 'copay', 'copayment', 'maternity', 'reimbursement', 'plan', 'benefit',
    'declaration', 'declaration requirements', 'pre-existing conditions', 'existing conditions',
    # Explicit rich-field keywords
    'deductible', 'telemedicine', 'wellness', 'wellness benefits',
    # Arabic/Arabizi variants for supported fields and rich fields
    'انيوال ليمت', 'حد سنوي', 'الحد السنوي', 'الحد الأقصى السنوي', 'السقف السنوي', 'مغطى', 'تغطية', 'شبكة', 'حمل', 'ماتيرنيتي', 'منطقة التغطية', 'ريمدي', 'ريميدي', 'خطة', 'بلان', 'مستشفى', 'عيادة', 'موجود', 'فيها', 'مغطى', 'مستشفيات', 'عيادات',
    # Arabic/Arabizi for deductible, telemedicine, wellness
    'خصم', 'ديكتبل', 'ديكتبل', 'ديكتابيليتي', 'تيليمديسن', 'تيليمديسين', 'استشارة عن بعد', 'العافية', 'ويلنس', 'فوائد العافية', 'فوائد ويلنس',
    # Phase 3: expanded Arabic Telegram-style phrasing
    'الحد', 'الليمت', 'ليمت', 'كم الحد', 'شو الحد',
    'التغطية', 'التغطيه', 'فوائد', 'المزايا', 'مزايا', 'يغطي', 'تشمل', 'فيه',
    'نطاق التغطية', 'التغطية الجغرافية', 'وين التغطية', 'اين التغطية', 'منطقه التغطيه',
    'ولادة', 'ولاده', 'تغطية الحمل', 'تغطية الولادة', 'الأمومة', 'أمومة', 'الامومة', 'امومة',
    'أسنان', 'الاسنان', 'الأسنان', 'اسنان', 'طبيب اسنان',
    'كوبي', 'كوباي', 'نسبة التحمل', 'تحمل المريض', 'نسبة المشاركة', 'حصة المريض',
    'استرداد', 'استرجاع', 'تعويض',
    'موافقة', 'موافقة مسبقة', 'تحويل', 'إحالة', 'احاله',
    'امراض سابقة', 'حالات سابقه', 'حالة سابقة',
    'اقرار', 'الاقرار', 'متطلبات الاقرار',
    'هل فيها', 'هل يغطي', 'هل تشمل', 'هل يشمل', 'شو', 'كم',
    'طوارئ', 'الطوارئ', 'تنويم', 'داخلي', 'صيدلية',
]
NETWORK_TERMS = [
    'provider', 'hospital', 'clinic', 'network', 'direct billing', 'is', 'in', 'part of', 'covered', 'accept', 'accepts',
    # Arabic/Arabizi
    'مستشفى', 'عيادة', 'شبكة', 'مباشر', 'موجود', 'في', 'تغطية', 'مغطى', 'مستشفيات', 'عيادات',
    # Phase 3: expanded Arabic network phrasing
    'ضمن الشبكة', 'في الشبكة', 'داخل الشبكة', 'خارج الشبكة',
    'ديركت بيلنج', 'فواتير مباشرة', 'دفع مباشر',
    'هل المستشفى', 'هل العيادة', 'موجوده',
]


def is_plan_query(q):
    qn = robust_normalize(q)
    return any(robust_normalize(attr) in qn for attr in PLAN_ATTRS)


def is_network_query(q):
    qn = robust_normalize(q)
    # Route direct billing questions to network lookup
    if 'direct billing' in qn or 'direct' in qn or 'مباشر' in qn or 'ديركت بيلنج' in qn or 'فواتير مباشرة' in qn:
        return True
    # Arabic in-network / out-of-network phrasing
    if 'داخل الشبكة' in qn or 'خارج الشبكة' in qn or 'ضمن الشبكة' in qn or 'في الشبكة' in qn or 'ضمن شبكة' in qn:
        return True
    # Heuristic: if question asks about a provider in a network/plan (Arabic/English)
    if any(robust_normalize(term) in qn for term in NETWORK_TERMS) and (('network' in qn or 'plan' in qn or 'شبكة' in qn or 'خطة' in qn or 'الشبكة' in qn)):
        return True
    # Or if it starts with 'is' or 'هل' and mentions a provider
    if re.match(r'(is|هل) [\w\s\u0600-\u06FF]+ (in|في)', qn):
        return True
    return False

# Hotfix Issue 6: unlimited qualifier — prepend denial when query claims "unlimited" but answer has a cap
def _apply_unlimited_check(qn, answer_text):
    """If the query asks about 'unlimited' and the answer contains a cap indicator, prepend denial."""
    unlimited_terms = ['unlimited', 'غير محدود', 'بدون حد', 'open limit', 'no limit', 'بلا حد']
    if not any(t in qn for t in unlimited_terms):
        return answer_text
    cap_indicators = ['aed', 'per year', 'per incident', 'up to', 'limited to', 'maximum', 'cap', 'limit']
    ans_lower = answer_text.lower()
    if any(ind in ans_lower for ind in cap_indicators):
        return f"No, it is not unlimited. {answer_text}"
    return answer_text

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ask a question against the insurance knowledge base.")
    parser.add_argument('question', nargs='+', help='Question to ask')
    args = parser.parse_args()
    question = ' '.join(args.question)

    # EARLY GUARD: If telemedicine is mentioned and explicit unsupported Remedy plan is present, block immediately
    import re
    telemed_terms_guard = ['telemedicine', 'تيلي ميديسن', 'تيليمديسن', 'استشارة عن بعد']
    plan_regex_guard = r"remedy[\s\-_]?(\d{2,})"
    if any(term in question.lower() for term in telemed_terms_guard):
        plan_match_guard = re.search(plan_regex_guard, question.lower())
        if plan_match_guard and plan_match_guard.group(1) not in ("02", "03", "04", "05", "06"):
            print("No answer found.")
            return

    import argparse
    parser = argparse.ArgumentParser(description="Ask a question against the insurance knowledge base.")
    parser.add_argument('question', nargs='+', help='Question to ask')
    args = parser.parse_args()
    question = ' '.join(args.question)

    plan_terms = [
        'remedy', 'ريمدي', 'ريميدي', 'plan', 'خطة', 'بلان',
        'classic', 'كلاسيك',
    ]

    qn = robust_normalize(question)

    # MINI PATCH: explicit benefit/rule/intent/alias expansion for Remedy 02
    # 1. Explicit benefit routing for Remedy 02
    # Minimal patch: route non-urgent inpatient approval queries to plan_lookup.py
    if 'non-urgent inpatient' in qn or 'non urgent inpatient' in qn or 'غير طارئة' in qn:
        plan_result = lookup_plan(question)
        if plan_result and plan_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(plan_result['answer'])}")
            return

    # Guard: if query explicitly names a non-Remedy plan family, bypass Remedy benefit shortcuts.
    # Uses centralized alias policy from src/plan_alias_policy.py.
    _resolved_id, _resolved_status = resolve_plan_alias(qn)
    # Deployment scope guardrail: confirmed plan outside approved scope → safe fallback
    if _resolved_status == "confirmed" and _resolved_id and _resolved_id not in DEPLOYMENT_APPROVED_PLANS:
        print("No answer found.")
        return
    if _resolved_status == "confirmed" and _resolved_id and not _resolved_id.startswith("REMEDY_"):
        plan_result = lookup_plan(question)
        if plan_result and plan_result.get('status') == 'found':
            print(f"[PLAN] {_apply_unlimited_check(qn, clean_output(plan_result['answer']))}")
            return
    elif _resolved_status == "excluded":
        print("No answer found.")
        return
    elif _resolved_status == "unrecognized_remedy":
        print("No answer found.")
        return

    benefit_patterns = [
        (['physiotherapy', 'علاج طبيعي', 'العلاج الطبيعي'], {"02": "Does Remedy 02 include physiotherapy?", "03": "Does Remedy 03 include physiotherapy?", "04": "Does Remedy 04 include physiotherapy?", "05": "Does Remedy 05 include physiotherapy?", "06": "Does Remedy 06 include physiotherapy?"}),
        (['dental', 'أسنان', 'تغطية أسنان', 'الأسنان', 'الاسنان', 'dental coverage', 'dental benefit', 'dental included', 'dental covered', 'هل فيها أسنان', 'هل الخطة فيها تغطية أسنان', 'هل dental موجودة'], {"02": "Does Remedy 02 include dental?", "03": "Does Remedy 03 include dental?", "04": "Does Remedy 04 include dental?", "05": "Does Remedy 05 include dental?", "06": "Does Remedy 06 include dental?"}),
        (['mri', 'magnetic resonance', 'تصوير بالرنين', 'الرنين المغناطيسي', 'رنين مغناطيسي', 'الرنين', 'رنين'], {"02": "Does Remedy 02 include MRI?", "03": "Does Remedy 03 include MRI?", "04": "Does Remedy 04 include MRI?", "05": "Does Remedy 05 include MRI?", "06": "Does Remedy 06 include MRI?"}),
        (['ct scan', 'computed tomography', 'سي تي', 'تصوير مقطعي'], {"02": "Does Remedy 02 include CT scan?", "03": "Does Remedy 03 include CT scan?", "04": "Does Remedy 04 include CT scan?", "05": "Does Remedy 05 include CT scan?", "06": "Does Remedy 06 include CT scan?"}),
        (['endoscopy', 'منظار', 'تنظير'], {"02": "Does Remedy 02 include endoscopy?", "03": "Does Remedy 03 include endoscopy?", "04": "Does Remedy 04 include endoscopy?", "05": "Does Remedy 05 include endoscopy?", "06": "Does Remedy 06 include endoscopy?"}),
        (['laboratory', 'lab test', 'تحاليل', 'اختبار معملي'], {"02": "Does Remedy 02 include laboratory tests?", "03": "Does Remedy 03 include laboratory tests?", "04": "Does Remedy 04 include laboratory tests?", "05": "Does Remedy 05 include laboratory tests?", "06": "Does Remedy 06 include laboratory tests?"}),
        (['radiology', 'تشخيص بالأشعة', 'تصوير شعاعي'], {"02": "Does Remedy 02 include radiology?", "03": "Does Remedy 03 include radiology?", "04": "Does Remedy 04 include radiology?", "05": "Does Remedy 05 include radiology?", "06": "Does Remedy 06 include radiology?"}),
        (['generic prescribed drugs', 'generic drugs', 'أدوية جنيسة', 'أدوية موصوفة', 'prescribed drugs'], {"02": "Does Remedy 02 include prescribed drugs?", "03": "What is the prescribed drugs cover for Remedy 03?", "04": "What is the prescribed drugs cover for Remedy 04?", "05": "What is the prescribed drugs cover for Remedy 05?", "06": "What is the prescribed drugs cover for Remedy 06?"}),
        (['optical', 'نظارات', 'بصريات', 'optical benefit', 'optical coverage'], {"02": "Does Remedy 02 include optical?", "03": "Does Remedy 03 include optical?", "04": "Does Remedy 04 include optical?", "05": "Does Remedy 05 include optical?", "06": "Does Remedy 06 include optical?"}),  # Optical = discount-only (25%)
        (['shingrix', 'shingrix vaccine', 'شينجريكس'], {"02": "Does Remedy 02 include Shingrix vaccine?", "03": "Does Remedy 03 include Shingrix vaccine?", "04": "Does Remedy 04 include Shingrix vaccine?", "05": "Does Remedy 05 include Shingrix vaccine?", "06": "Does Remedy 06 include Shingrix vaccine?"}),  # Shingrix: R06 only
        (['influenza', 'influenza vaccine', 'flu vaccine', 'flu shot', 'لقاح الانفلونزا', 'تطعيم الانفلونزا'], {"02": "Does Remedy 02 include influenza vaccine?", "03": "Does Remedy 03 include influenza vaccine?", "04": "Does Remedy 04 include influenza vaccine?", "05": "Does Remedy 05 include influenza vaccine?", "06": "Does Remedy 06 include influenza vaccine?"}),
        (['pneumococcal', 'pneumococcal vaccine', 'لقاح المكورات'], {"02": "Does Remedy 02 include pneumococcal vaccine?", "03": "Does Remedy 03 include pneumococcal vaccine?", "04": "Does Remedy 04 include pneumococcal vaccine?", "05": "Does Remedy 05 include pneumococcal vaccine?", "06": "Does Remedy 06 include pneumococcal vaccine?"}),
        (['vaccine', 'vaccination', 'immunization', 'تطعيم', 'لقاح', 'تطعيمات'], {"02": "Does Remedy 02 include vaccines?", "03": "Does Remedy 03 include vaccines?", "04": "Does Remedy 04 include vaccines?", "05": "Does Remedy 05 include vaccines?", "06": "Does Remedy 06 include vaccines?"}),
    ]
    # Skip benefit routing if query has approval intent (let rule_patterns handle it)
    approval_intent_terms = ['require approval', 'approval required', 'approval for', 'need approval', 'pre-approval', 'preapproval', 'require pre approval', 'موافقة مسبقة', 'محتاج موافقة', 'محتاج approval', 'يحتاج موافقة']
    has_approval_intent = any(robust_normalize(term) in qn for term in approval_intent_terms)

    for terms, routed_qs in benefit_patterns:
        if has_approval_intent:
            break
        if any(robust_normalize(term) in qn for term in terms):
            # Determine explicit plan
            plan = None
            if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
                plan = "06"
            elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
                plan = "05"
            elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
                plan = "04"
            elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
                plan = "03"
            elif 'remedy 02' in qn or 'remedy02' in qn or 'ريمدي 02' in qn or 'ريميدي 02' in qn or '02' in qn:
                plan = "02"
            # Default to Remedy 02 if not explicit
            if not plan:
                plan = "02"
            routed_q = routed_qs.get(plan)
            if routed_q:
                benefit_result = lookup_plan(routed_q)
                if benefit_result and benefit_result.get('status') == 'found':
                    print(f"[PLAN] {_apply_unlimited_check(qn, clean_output(benefit_result['answer']))}")
                    return

    # 2. Explicit maternity intent split
    # Hotfix: expand Arabic WP variants — "فترة انتظار" (no الـ), "مدة انتظار", "انتظار الحمل"
    if 'waiting period' in qn or 'فترة الانتظار' in qn or 'فترة انتظار' in qn or 'مدة انتظار' in qn or 'انتظار الحمل' in qn:
        if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
            mat_result = lookup_plan("What is the maternity waiting period for Remedy 06?")
        elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
            mat_result = lookup_plan("What is the maternity waiting period for Remedy 05?")
        elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
            mat_result = lookup_plan("What is the maternity waiting period for Remedy 04?")
        elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            mat_result = lookup_plan("What is the maternity waiting period for Remedy 03?")
        else:
            mat_result = lookup_plan("What is the maternity waiting period for Remedy 02?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(mat_result['answer'])}")
            return
    if 'prenatal' in qn or 'ما قبل الولادة' in qn:
        if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
            mat_result = lookup_plan("Does Remedy 06 include prenatal services?")
        elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
            mat_result = lookup_plan("Does Remedy 05 include prenatal services?")
        elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
            mat_result = lookup_plan("Does Remedy 04 include prenatal services?")
        elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            mat_result = lookup_plan("Does Remedy 03 include prenatal services?")
        else:
            mat_result = lookup_plan("Does Remedy 02 include prenatal services?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(mat_result['answer'])}")
            return
    if 'newborn' in qn or 'حديثي الولادة' in qn:
        if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
            mat_result = lookup_plan("Does Remedy 06 include newborn cover?")
        elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
            mat_result = lookup_plan("Does Remedy 05 include newborn cover?")
        elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
            mat_result = lookup_plan("Does Remedy 04 include newborn cover?")
        elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            mat_result = lookup_plan("Does Remedy 03 include newborn cover?")
        else:
            mat_result = lookup_plan("Does Remedy 02 include newborn cover?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(mat_result['answer'])}")
            return

    # 3. Telemedicine distinction — ISA Assist / travel only for all supported plans.
    # Telemedicine is NOT a standalone OP benefit; it's bundled under ISA Assist.
    telemed_terms = [
        'telemedicine', 'تيلي ميديسن', 'تيليمديسن', 'التلي ميديسن', 'استشارة عن بعد'
    ]
    if any(robust_normalize(term) in qn for term in telemed_terms):
        # Distinguish local vs. ISA Assist
        if 'isa assist' in qn or 'travel' in qn or 'سفر' in qn:
            print("[PLAN] Telemedicine is available under ISA Assist / travel assistance for Remedy 02 while traveling outside country of residence.")
            return
        # Detect which Remedy plan
        if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
            telemed_result = lookup_plan("Does Remedy 06 include telemedicine?")
        elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
            telemed_result = lookup_plan("Does Remedy 05 include telemedicine?")
        elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
            telemed_result = lookup_plan("Does Remedy 04 include telemedicine?")
        elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            telemed_result = lookup_plan("Does Remedy 03 include telemedicine?")
        else:
            telemed_result = lookup_plan("Does Remedy 02 include telemedicine?")
        if telemed_result and telemed_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(telemed_result['answer'])} (Telemedicine is available under ISA Assist while traveling.)")
            return

    # 4. GP referral, pre-existing, chronic, approval-required rules
    # Hotfix: added Arabic direct-access terms and bare 'specialist' for referral routing
    rule_patterns = [
        (['gp referral', 'specialist referral', 'referral', 'تحويل', 'المختص', 'طبيب مختص', 'الطبيب المختص', 'إحالة طبيب عام', 'إحالة أخصائي', 'دخول مباشر', 'specialist', 'دكتور متخصص', 'طبيب متخصص', 'محتاج تحويل', 'محتاجة تحويل', 'لازم gp', 'احاله', 'إحالة', 'تحويل طبيب'], "Do I need GP referral for specialist consultation in Remedy XX?"),
        (['pre-existing', 'pre existing', 'chronic', 'existing condition', 'حالة مزمنة', 'حالات مزمنة', 'حالة سابقة', 'preexisting', 'امراض سابقة', 'حالات سابقه', 'مرض مزمن', 'حالة مسبقة'], "What are the pre-existing condition rules for Remedy XX?"),
        (['approval required', 'approval', 'موافقة', 'موافقة مسبقة', 'محتاج موافقة', 'يحتاج موافقة', 'لازم موافقة', 'بري ابروفال', 'pre approval'], "Is approval required for Remedy XX?")
    ]
    for terms, routed_q in rule_patterns:
        if any(robust_normalize(term) in qn for term in terms):
            from rules_lookup import lookup_rules
            # Patch: route to Remedy 04 if query mentions Remedy 04, Remedy 03 if mentions 03, else Remedy 02
            if 'remedy 06' in qn or 'remedy06' in qn or 'ريمدي 06' in qn or 'ريميدي 06' in qn:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 06')
            elif 'remedy 05' in qn or 'remedy05' in qn or 'ريمدي 05' in qn or 'ريميدي 05' in qn:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 05')
            elif 'remedy 04' in qn or 'remedy04' in qn or 'ريمدي 04' in qn or 'ريميدي 04' in qn:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 04')
            elif 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 03')
            else:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 02')
            # Narrow: if approval + MRI, pass MRI context to rules lookup
            mri_ar_terms = ['mri', 'الرنين', 'رنين']
            if any(t in qn for t in mri_ar_terms) and any(robust_normalize(t) in qn for t in ['approval', 'موافقة']):
                routed_q = routed_q.replace('Is approval required', 'Is MRI pre-approval required')
            rule_result = lookup_rules(routed_q)
            if rule_result and rule_result.get('status') == 'found':
                print(f"[RULE] {clean_output(rule_result['answer'])}")
                return

    # MINI PHASE 3C: maternity-only no-plan fallback
    # If the query does NOT mention any plan and is a clear maternity question, default to Remedy 02
    maternity_terms = [
        'maternity', 'حمل', 'ماتيرنيتي', 'ولادة', 'الأمومة', 'أمومة', 'الامومة', 'امومة', 'maternity coverage', 'maternity benefit', 'maternity included', 'maternity covered', 'هل فيها حمل', 'هل الخطة فيها ولادة', 'هل maternity موجودة'
    ]
    if (
        any(robust_normalize(term) in qn for term in maternity_terms)
        and not any(robust_normalize(term) in qn for term in plan_terms)
    ):
        maternity_result = lookup_plan("Does Remedy 02 include maternity?")
        if maternity_result and maternity_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(maternity_result['answer'])}")
            return

    # MINI PHASE 3B: telemedicine-only no-plan fallback
    # If the query does NOT mention any plan and is a clear telemedicine question, default to Remedy 02
    telemed_terms = [
        'telemedicine', 'تيلي ميديسن', 'تيليمديسن', 'استشارة عن بعد'
    ]
    if any(robust_normalize(term) in qn for term in telemed_terms):
        import re
        # Check both raw and normalized query for explicit plan mention
        plan_regex = r"remedy[\s\-_]?(\d{2,})"
        plan_match_raw = re.search(plan_regex, question.lower())
        plan_match_norm = re.search(plan_regex, qn)
        plan_match = plan_match_raw or plan_match_norm
        if plan_match:
            plan_num = plan_match.group(1)
            if plan_num not in ("02", "03", "04", "05", "06"):
                # Minimal guard: block fallback if explicit unsupported plan and plan lookup did not resolve
                plan_result = lookup_plan(question)
                if not (plan_result and plan_result.get('status') == 'found'):
                    print("No answer found.")
                    return
            # If explicit Remedy 02, allow normal flow (will be handled by plan lookup above)
        else:
            telemed_result = lookup_plan("Does Remedy 02 include telemedicine?")
            if telemed_result and telemed_result.get('status') == 'found':
                print(f"[PLAN] {clean_output(telemed_result['answer'])}")
                return

    # MINI PHASE 3A: physiotherapy-only no-plan fallback
    # If the query does NOT mention any plan and is a clear physiotherapy question, default to Remedy 02
    physio_terms = [
        'physiotherapy', 'علاج طبيعي', 'العلاج الطبيعي'
    ]
    if (
        any(robust_normalize(term) in qn for term in physio_terms)
        and not any(robust_normalize(term) in qn for term in plan_terms)
    ):
        # Route to explicit Remedy 02 physiotherapy answer (fallback only if no plan mentioned)
        physio_result = lookup_plan("Does Remedy 02 cover physiotherapy?")
        if physio_result and physio_result.get('status') == 'found':
            print(f"[PLAN] {clean_output(physio_result['answer'])}")
            return


    # Provider-specific network routing — intercept BEFORE plan_lookup when query
    # mentions a known provider (or alias) AND has network/direct-billing intent.
    # This prevents generic plan network descriptions from answering provider-specific questions.
    import re as _re
    from network_lookup import _load_providers as _lp, _load_aliases as _la, robust_normalize as _rnorm

    # Build lookup tables (small CSV — 11 providers, 18 aliases)
    _all_providers = _lp()
    _all_aliases = _la()
    _provider_names = [_rnorm(r.get('provider_name', '')) for r in _all_providers]

    # Detect if a known provider name or alias appears in the query
    _detected_provider_display = None
    for _alias_norm, _canonical in _all_aliases.items():
        if _alias_norm and _alias_norm in qn:
            _detected_provider_display = _canonical
            break
    if not _detected_provider_display:
        for _row in _all_providers:
            if _rnorm(_row.get('provider_name', '')) in qn:
                _detected_provider_display = _row.get('provider_name', '')
                break
    # Reverse partial: query contains a significant prefix of a provider name (e.g. "Aster Hospital")
    if not _detected_provider_display:
        for _row in _all_providers:
            _pn = _rnorm(_row.get('provider_name', ''))
            _pn_words = _pn.split()
            # Check if at least 2 leading words of the provider name appear consecutively in the query
            if len(_pn_words) >= 2:
                _prefix = ' '.join(_pn_words[:2])
                if _prefix in qn:
                    _detected_provider_display = _row.get('provider_name', '')
                    break

    # Network / direct-billing intent phrases (broader than just "in the network")
    _network_intent_phrases = [
        'in the network', 'in network', 'part of the network', 'part of network',
        'covered under', 'covered by', 'on the network', 'within the network',
        'direct billing', 'offer direct', 'direct bill',
        # Arabic
        'ضمن الشبكة', 'ضمن شبكة', 'في الشبكة', 'في شبكة', 'داخل الشبكة', 'داخل شبكة',
        'خارج الشبكة', 'ديركت بيلنج', 'ديرکت بيلنج', 'مباشر',
    ]
    _has_network_intent = any(p in qn for p in _network_intent_phrases)

    if _detected_provider_display and (_has_network_intent or is_network_query(question)):
        net_result = lookup_network(question)
        _matched_provider = (net_result or {}).get('provider', '')
        _stop = {'the', 'a', 'al', 'hospital', 'clinic', 'center', 'centre'}
        _req_words = set(_rnorm(_detected_provider_display).split()) - _stop
        _match_words = set(_rnorm(_matched_provider).split()) - _stop
        _provider_confirmed = bool(_req_words & _match_words) if _req_words and _match_words else False
        if net_result and net_result.get('status') == 'found' and _provider_confirmed:
            print(f"[NETWORK] {clean_output(net_result['answer'])}")
            return
        # Provider not found or false match → safe negative verdict
        _plan_match = _re.search(r'remedy[\s\-_]?(\d{2,})', qn)
        _plan_label = f"Remedy {_plan_match.group(1)}" if _plan_match else "this plan"
        print(f"[NETWORK] {_detected_provider_display} is not confirmed in the provider network for {_plan_label}. Please verify directly with NGI or the provider.")
        return

    # Fallback: unknown provider name extracted via regex (not in our data)
    _provider_in_network = _re.search(r'is\s+(.+?)\s+in\s+(?:the\s+)?(?:network|provider)', qn)
    if not _provider_in_network:
        _provider_in_network = _re.search(r'(?:does|can|is)\s+(.+?)\s+(?:offer|provide|have|accept)\s+(?:direct\s+billing|direct\s+bill)', qn)
    if not _provider_in_network:
        _provider_in_network = _re.search(r'هل\s+(.+?)\s+(?:ضمن|في|داخل)\s+(?:شبكة|الشبكة)', qn)
    if _provider_in_network and (_has_network_intent or is_network_query(question)):
        _requested_provider = _provider_in_network.group(1).strip()
        _plan_match = _re.search(r'remedy[\s\-_]?(\d{2,})', qn)
        _plan_label = f"Remedy {_plan_match.group(1)}" if _plan_match else "this plan"
        print(f"[NETWORK] {_requested_provider.title()} is not confirmed in the provider network for {_plan_label}. Please verify directly with NGI or the provider.")
        return

    # 1. Plan lookup
    if is_plan_query(question):
        plan_result = lookup_plan(question)
        # Special handling for ambiguous copay/coplan queries
        if (
            ("copay" in question.lower() or "copayment" in question.lower())
            and (not any(x in question.lower() for x in ["remedy", "plan "]))
            and (plan_result is None or plan_result.get("status") != "found")
        ):
            print("Please specify the plan name for copayment details (e.g., 'What is the copay for Remedy 02?').")
            return
        if plan_result and plan_result.get('status') == 'found':
            print(f"[PLAN] {_apply_unlimited_check(qn, clean_output(plan_result['answer']))}")
            return

    # 2. Network lookup
    if is_network_query(question):
        net_result = lookup_network(question)
        if net_result and net_result.get('status') == 'found':
            print(f"[NETWORK] {clean_output(net_result['answer'])}")
            return
        # Clarification: generic network / direct billing query without a specific provider
        # Skip if the user is asking for FAQ content (not an actual network lookup)
        _is_faq_intent = 'faq' in qn or 'frequently asked' in qn
        if not _is_faq_intent:
            _direct_billing_terms = ["direct billing", "direct bill", "مباشر", "ديركت بيلنج", "ديرکت بيلنج"]
            if any(t in qn for t in _direct_billing_terms):
                print("[NETWORK] Please provide the hospital or clinic name so I can check whether direct billing is available.\nيرجى تزويدنا باسم المستشفى أو العيادة حتى نتمكن من التحقق من توفر الدفع المباشر.")
                return
            _network_generic_terms = [
                "network", "hospital", "clinic", "provider", "in network",
                "الشبكة", "ضمن الشبكة", "في الشبكة", "خارج الشبكة", "مستشفى", "عيادة",
                "دكتور", "طبيب",
            ]
            if any(t in qn for t in _network_generic_terms):
                print("[NETWORK] Please provide the hospital or clinic name so I can check whether it is in the network.\nيرجى تزويدنا باسم المستشفى أو العيادة حتى نتمكن من التحقق من وجودها ضمن الشبكة.")
                return

    # 3. FAQ/training fallback
    answer = lookup_training_qa(question, TRAINING_QA_CSV)
    if answer:
        print(f"[FAQ] {clean_output(answer)}")
        return

    print("No answer found.")


if __name__ == '__main__':
    main()