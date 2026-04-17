from __future__ import annotations


from benefit_lookup import lookup_benefit
from faq_lookup import lookup_faq
from network_lookup import lookup_network
from plan_lookup import lookup_plan
from rules_lookup import lookup_rules
from training_lookup import search_training_records
from plan_alias_policy import CLASSIC_PLAN_RE, REMEDY_PLAN_RE, CONFIRMED_CLASSIC_IDS, CONFIRMED_REMEDY_IDS


FAQ_HINTS = [
    "how do i",
    "why was",
    "what happens",
    "i can't",
    "what should i do",
    "what qualifies",
    "difference between",
    "كيف",
    "ليش",
    "شو لازم",
    "شو اسوي",
    "الفرق بين",
    "ما الفرق",
]

PLAN_HINTS = [
    "annual limit",
    "الحد السنوي",
    "الحد الأقصى السنوي",
    "السقف السنوي",
    "حد سنوي",
    "كم الحد",
    "شو الحد",
    "الليمت",
    "area of coverage",
    "منطقة التغطية",
    "نطاق التغطية",
    "وين التغطية",
    "مناطق التغطية",
    "plan type",
    "provider network",
    "remedy 02",
    "remedy 03",
    "remedy 04",
    "remedy 05",
    "remedy 06",
    "remedy_02",
    "remedy_03",
    "remedy_04",
    "remedy_05",
    "remedy_06",
    "ريمدي",
    "ريميدي",
    "classic plan",
    "classic 1r",
    "classic 2r",
    "classic 2",
    "classic 3",
    "classic 4",
    "hn_classic",
    "hn classic",
    "كلاسيك",
    "كوبي",
    "نسبة التحمل",
    "copay",
    "copayment",
    "التغطية",
    "فوائد",
    "المزايا",
    "استرداد",
    "تعويض",
    "reimbursement",
]

BENEFIT_HINTS = [
    "benefit",
    "coverage for",
    "mental health",
    "maternity services",
    "vaccination",
    "influenza vaccine",
    "organ transplantation",
    "kidney dialysis",
    "room and board",
    "room & board",
    "physiotherapy",
    "isa assist",
    "حمل",
    "ولادة",
    "تغطية الحمل",
    "أسنان",
    "الاسنان",
    "تطعيم",
    "لقاح",
    "تطعيمات",
    "علاج طبيعي",
    "صحة نفسية",
    "زراعة أعضاء",
    "غسيل كلى",
    "أدوية",
    "عمليات",
    "تنويم",
    "إقامة",
    "نظارات",
    "بصريات",
]

NETWORK_HINTS = [
    "in network",
    "provider",
    "hospital",
    "clinic",
    "doctor",
    "aster",
    "burjeel",
    "ajman specialty",
    "international modern",
    "al saha",
    "أستر",
    "القصيص",
    "الشبكة",
    "ضمن الشبكة",
    "في الشبكة",
    "خارج الشبكة",
    "مستشفى",
    "عيادة",
    "دكتور",
    "طبيب",
    "ديركت بيلنج",
    "مباشر",
]

RULE_HINTS = [
    "approval rule",
    "referral",
    "reimbursement",
    "exclusion",
    "terms",
    "condition",
    "direct billing",
    "outside uae",
    "outside network",
    "pre existing",
    "تحويل",
    "إحالة",
    "موافقة",
    "موافقة مسبقة",
    "استثناء",
    "استثناءات",
    "حالة مزمنة",
    "حالات مزمنة",
    "امراض سابقة",
    "خارج الامارات",
    "خارج الشبكة",
    "بري ابروفال",
]


def route_question(query: str) -> str:
    lowered = query.lower()

    if any(hint in lowered for hint in BENEFIT_HINTS):
        return "benefit_lookup"
    if any(hint in lowered for hint in PLAN_HINTS):
        return "plan_lookup"
    if any(hint in lowered for hint in NETWORK_HINTS) and not any(hint in lowered for hint in FAQ_HINTS):
        return "network_lookup"
    if any(hint in lowered for hint in RULE_HINTS) and not any(hint in lowered for hint in FAQ_HINTS):
        return "rules_lookup"
    if any(hint in lowered for hint in FAQ_HINTS):
        return "faq_lookup"
    return "faq_lookup"


def dispatch_query(query: str) -> dict[str, str]:
    """Central dispatcher. Supported scope: Remedy 02-06. Plan gate is in plan_lookup.py."""
    route = route_question(query)
    # 1. Structured lookups (priority)
    if route == "plan_lookup":
        result = lookup_plan(query)
        if result is None:
            result = {"status": "not_found"}
        if result.get("status") == "found":
            return result
    if route == "benefit_lookup":
        # Extract plan and intent from query (simple heuristic)
        import re
        # Match supported plans: Remedy 02-06 and HN Classic plans.
        plan_match = REMEDY_PLAN_RE.search(query)
        classic_match = CLASSIC_PLAN_RE.search(query)
        if plan_match:
            plan = f"REMEDY_{plan_match.group(1)}"
            if plan not in CONFIRMED_REMEDY_IDS:
                plan = None
        elif classic_match:
            plan = f"HN_CLASSIC_{classic_match.group(1).upper()}"
            if plan not in CONFIRMED_CLASSIC_IDS:
                plan = None
        else:
            plan = None
        # Try to extract intent by matching known benefit keywords
        from benefit_lookup import BENEFIT_KEYWORDS
        lowered = query.lower()
        intent = None
        for key, variants in BENEFIT_KEYWORDS.items():
            for v in variants:
                if v in lowered:
                    intent = v
                    break
            if intent:
                break
        if plan and intent:
            benefit_row = lookup_benefit(plan, intent)
            if benefit_row:
                return {"status": "found", "route": "benefit_lookup", "plan": plan, "intent": intent, "benefit": benefit_row}
        # Fallback: if benefit_lookup failed and query mentions a plan, try plan_lookup
        if plan_match:
            result = lookup_plan(query)
            if result is None:
                result = {"status": "not_found"}
            if result.get("status") == "found":
                return result
    if route == "network_lookup":
        result = lookup_network(query)
        if result.get("status") == "found":
            return result
        # Clarification patch: generic network / direct billing queries without a specific provider
        lowered_q = query.lower()
        _direct_billing_terms = ["direct billing", "direct bill", "مباشر", "ديركت بيلنج", "ديرکت بيلنج"]
        _is_direct_billing = any(t in lowered_q for t in _direct_billing_terms)
        if _is_direct_billing:
            return {
                "status": "clarification",
                "route": "network_lookup",
                "answer": (
                    "Please provide the hospital or clinic name so I can check whether direct billing is available.\n"
                    "يرجى تزويدنا باسم المستشفى أو العيادة حتى نتمكن من التحقق من توفر الدفع المباشر."
                ),
            }
        # Generic network query (mentions hospital/clinic/network but no specific provider)
        _network_generic_terms = [
            "network", "hospital", "clinic", "provider", "in network", "in-network",
            "الشبكة", "ضمن الشبكة", "في الشبكة", "خارج الشبكة", "مستشفى", "عيادة",
            "دكتور", "طبيب",
        ]
        if any(t in lowered_q for t in _network_generic_terms):
            return {
                "status": "clarification",
                "route": "network_lookup",
                "answer": (
                    "Please provide the hospital or clinic name so I can check whether it is in the network.\n"
                    "يرجى تزويدنا باسم المستشفى أو العيادة حتى نتمكن من التحقق من وجودها ضمن الشبكة."
                ),
            }
    if route == "rules_lookup":
        result = lookup_rules(query)
        if result.get("status") == "found":
            return result
    # 2. FAQ lookup
    faq_result = lookup_faq(query)
    if faq_result.get("status") == "found":
        return faq_result
    # 3. Training fallback (only if all above fail)
    training_matches = search_training_records(query)
    if training_matches:
        # Return the first match in a deterministic way
        match = training_matches[0]
        return {
            "status": "training_fallback",
            "route": "training_lookup",
            "matched_question": match["question"],
            "answer": match["answer"],
            "category": match["category"],
            "lang": match["lang"],
            "plan_id": match["plan_id"],
            "source": match["source"],
        }
    # 4. No answer fallback
    return {
        "status": "not_found",
        "route": "router",
        "message": "No structured or training answer found."
    }