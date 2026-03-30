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