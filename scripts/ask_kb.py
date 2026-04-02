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

PLAN_ATTRS = [
    'annual limit', 'annual_max', 'limit', 'area of coverage', 'coverage', 'network', 'copay', 'copayment', 'maternity', 'reimbursement', 'plan', 'benefit',
    'declaration', 'declaration requirements', 'pre-existing conditions', 'existing conditions',
    # Explicit rich-field keywords
    'deductible', 'telemedicine', 'wellness', 'wellness benefits',
    # Arabic/Arabizi variants for supported fields and rich fields
    'انيوال ليمت', 'حد سنوي', 'مغطى', 'تغطية', 'شبكة', 'حمل', 'ماتيرنيتي', 'منطقة التغطية', 'ريمدي', 'ريميدي', 'خطة', 'بلان', 'مستشفى', 'عيادة', 'موجود', 'فيها', 'مغطى', 'مستشفيات', 'عيادات',
    # Arabic/Arabizi for deductible, telemedicine, wellness
    'خصم', 'ديكتبل', 'ديكتبل', 'ديكتابيليتي', 'تيليمديسن', 'تيليمديسين', 'استشارة عن بعد', 'العافية', 'ويلنس', 'فوائد العافية', 'فوائد ويلنس'
]
NETWORK_TERMS = [
    'provider', 'hospital', 'clinic', 'network', 'direct billing', 'is', 'in', 'part of', 'covered', 'accept', 'accepts',
    # Arabic/Arabizi
    'مستشفى', 'عيادة', 'شبكة', 'مباشر', 'موجود', 'في', 'تغطية', 'مغطى', 'مستشفيات', 'عيادات'
]


def is_plan_query(q):
    qn = robust_normalize(q)
    return any(robust_normalize(attr) in qn for attr in PLAN_ATTRS)


def is_network_query(q):
    qn = robust_normalize(q)
    # Route direct billing questions to network lookup
    if 'direct billing' in qn or 'direct' in qn or 'مباشر' in qn:
        return True
    # Heuristic: if question asks about a provider in a network/plan (Arabic/English)
    if any(robust_normalize(term) in qn for term in NETWORK_TERMS) and (('network' in qn or 'plan' in qn or 'شبكة' in qn or 'خطة' in qn)):
        return True
    # Or if it starts with 'is' or 'هل' and mentions a provider
    if re.match(r'(is|هل) [\w\s\u0600-\u06FF]+ (in|في)', qn):
        return True
    return False

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
        if plan_match_guard and plan_match_guard.group(1) != "02":
            print("No answer found.")
            return

    import argparse
    parser = argparse.ArgumentParser(description="Ask a question against the insurance knowledge base.")
    parser.add_argument('question', nargs='+', help='Question to ask')
    args = parser.parse_args()
    question = ' '.join(args.question)

    plan_terms = [
        'remedy', 'ريمدي', 'ريميدي', 'plan', 'خطة', 'بلان'
    ]

    qn = robust_normalize(question)

    # MINI PATCH: explicit benefit/rule/intent/alias expansion for Remedy 02
    # 1. Explicit benefit routing for Remedy 02
    # Minimal patch: route non-urgent inpatient approval queries to plan_lookup.py
    if 'non-urgent inpatient' in qn or 'non urgent inpatient' in qn or 'غير طارئة' in qn:
        plan_result = lookup_plan(question)
        if plan_result and plan_result.get('status') == 'found':
            print(f"[PLAN] {plan_result['answer']}")
            return

    benefit_patterns = [
        (['physiotherapy', 'علاج طبيعي', 'العلاج الطبيعي'], {"02": "Does Remedy 02 include physiotherapy?", "03": "Does Remedy 03 include physiotherapy?"}),
        (['dental', 'أسنان', 'تغطية أسنان', 'dental coverage', 'dental benefit', 'dental included', 'dental covered', 'هل فيها أسنان', 'هل الخطة فيها تغطية أسنان', 'هل dental موجودة'], {"02": "Does Remedy 02 include dental?"}),
        (['mri', 'magnetic resonance', 'تصوير بالرنين'], {"02": "Does Remedy 02 include MRI?", "03": "Does Remedy 03 include MRI?"}),
        (['ct scan', 'computed tomography', 'سي تي', 'تصوير مقطعي'], {"02": "Does Remedy 02 include CT scan?", "03": "Does Remedy 03 include CT scan?"}),
        (['endoscopy', 'منظار', 'تنظير'], {"02": "Does Remedy 02 include endoscopy?", "03": "Does Remedy 03 include endoscopy?"}),
        (['laboratory', 'lab test', 'تحاليل', 'اختبار معملي'], {"02": "Does Remedy 02 include laboratory tests?", "03": "Does Remedy 03 include laboratory tests?"}),
        (['radiology', 'تشخيص بالأشعة', 'تصوير شعاعي'], {"02": "Does Remedy 02 include radiology?", "03": "Does Remedy 03 include radiology?"}),
        (['generic prescribed drugs', 'generic drugs', 'أدوية جنيسة', 'أدوية موصوفة', 'prescribed drugs'], {"02": "Does Remedy 02 include prescribed drugs?", "03": "What is the prescribed drugs cover for Remedy 03?"})
    ]
    for terms, routed_qs in benefit_patterns:
        if any(term in qn for term in terms):
            # Determine explicit plan
            plan = None
            if 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
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
                    print(f"[PLAN] {benefit_result['answer']}")
                    return

    # 2. Explicit maternity intent split
    if 'waiting period' in qn or 'فترة الانتظار' in qn:
        mat_result = lookup_plan("What is the maternity waiting period for Remedy 02?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {mat_result['answer']}")
            return
    if 'prenatal' in qn or 'ما قبل الولادة' in qn:
        if 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            mat_result = lookup_plan("Does Remedy 03 include prenatal services?")
        else:
            mat_result = lookup_plan("Does Remedy 02 include prenatal services?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {mat_result['answer']}")
            return
    if 'newborn' in qn or 'حديثي الولادة' in qn:
        if 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
            mat_result = lookup_plan("Does Remedy 03 include newborn cover?")
        else:
            mat_result = lookup_plan("Does Remedy 02 include newborn cover?")
        if mat_result and mat_result.get('status') == 'found':
            print(f"[PLAN] {mat_result['answer']}")
            return

    # 3. Telemedicine distinction
    telemed_terms = [
        'telemedicine', 'تيلي ميديسن', 'تيليمديسن', 'استشارة عن بعد'
    ]
    if any(term in qn for term in telemed_terms):
        # Distinguish local vs. ISA Assist
        if 'isa assist' in qn or 'travel' in qn or 'سفر' in qn:
            print("[PLAN] Telemedicine is available under ISA Assist / travel assistance for Remedy 02 while traveling outside country of residence.")
            return
        telemed_result = lookup_plan("Does Remedy 02 include telemedicine?")
        if telemed_result and telemed_result.get('status') == 'found':
            print(f"[PLAN] {telemed_result['answer']} (Note: Local telemedicine is not covered, but telemedicine is available under ISA Assist while traveling.)")
            return

    # 4. GP referral, pre-existing, chronic, approval-required rules
    rule_patterns = [
        (['gp referral', 'specialist referral', 'إحالة طبيب عام', 'إحالة أخصائي'], "Do I need GP referral for specialist consultation in Remedy XX?"),
        (['pre-existing', 'pre existing', 'chronic', 'existing condition', 'حالة مزمنة', 'حالات مزمنة', 'حالة سابقة', 'preexisting'], "What are the pre-existing condition rules for Remedy XX?"),
        (['approval required', 'approval', 'موافقة', 'موافقة مسبقة'], "Is approval required for Remedy XX?")
    ]
    for terms, routed_q in rule_patterns:
        if any(term in qn for term in terms):
            from rules_lookup import lookup_rules
            # Patch: route to Remedy 03 if query mentions Remedy 03, else Remedy 02
            if 'remedy 03' in qn or 'remedy03' in qn or 'ريمدي 03' in qn or 'ريميدي 03' in qn or '03' in qn:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 03')
            else:
                routed_q = routed_q.replace('Remedy XX', 'Remedy 02')
            rule_result = lookup_rules(routed_q)
            if rule_result and rule_result.get('status') == 'found':
                print(f"[RULE] {rule_result['answer']}")
                return

    # MINI PHASE 3C: maternity-only no-plan fallback
    # If the query does NOT mention any plan and is a clear maternity question, default to Remedy 02
    maternity_terms = [
        'maternity', 'حمل', 'ماتيرنيتي', 'ولادة', 'maternity coverage', 'maternity benefit', 'maternity included', 'maternity covered', 'هل فيها حمل', 'هل الخطة فيها ولادة', 'هل maternity موجودة'
    ]
    if (
        any(term in qn for term in maternity_terms)
        and not any(term in qn for term in plan_terms)
    ):
        maternity_result = lookup_plan("Does Remedy 02 include maternity?")
        if maternity_result and maternity_result.get('status') == 'found':
            print(f"[PLAN] {maternity_result['answer']}")
            return

    # MINI PHASE 3B: telemedicine-only no-plan fallback
    # If the query does NOT mention any plan and is a clear telemedicine question, default to Remedy 02
    telemed_terms = [
        'telemedicine', 'تيلي ميديسن', 'تيليمديسن', 'استشارة عن بعد'
    ]
    if any(term in qn for term in telemed_terms):
        import re
        # Check both raw and normalized query for explicit plan mention
        plan_regex = r"remedy[\s\-_]?(\d{2,})"
        plan_match_raw = re.search(plan_regex, question.lower())
        plan_match_norm = re.search(plan_regex, qn)
        plan_match = plan_match_raw or plan_match_norm
        if plan_match:
            plan_num = plan_match.group(1)
            if plan_num != "02":
                # Minimal guard: block fallback if explicit unsupported plan and plan lookup did not resolve
                plan_result = lookup_plan(question)
                if not (plan_result and plan_result.get('status') == 'found'):
                    print("No answer found.")
                    return
            # If explicit Remedy 02, allow normal flow (will be handled by plan lookup above)
        else:
            telemed_result = lookup_plan("Does Remedy 02 include telemedicine?")
            if telemed_result and telemed_result.get('status') == 'found':
                print(f"[PLAN] {telemed_result['answer']}")
                return

    # MINI PHASE 3A: physiotherapy-only no-plan fallback
    # If the query does NOT mention any plan and is a clear physiotherapy question, default to Remedy 02
    physio_terms = [
        'physiotherapy', 'علاج طبيعي', 'العلاج الطبيعي'
    ]
    if (
        any(term in qn for term in physio_terms)
        and not any(term in qn for term in plan_terms)
    ):
        # Route to explicit Remedy 02 physiotherapy answer (fallback only if no plan mentioned)
        physio_result = lookup_plan("Does Remedy 02 cover physiotherapy?")
        if physio_result and physio_result.get('status') == 'found':
            print(f"[PLAN] {physio_result['answer']}")
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
            print(f"[PLAN] {plan_result['answer']}")
            return

    # 2. Network lookup
    if is_network_query(question):
        net_result = lookup_network(question)
        if net_result and net_result.get('status') == 'found':
            print(f"[NETWORK] {net_result['answer']}")
            return

    # 3. FAQ/training fallback
    answer = lookup_training_qa(question, TRAINING_QA_CSV)
    if answer:
        print(f"[FAQ] {answer}")
        return

    print("No answer found.")


if __name__ == '__main__':
    main()