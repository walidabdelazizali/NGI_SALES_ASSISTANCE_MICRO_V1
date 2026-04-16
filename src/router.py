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
]

PLAN_HINTS = [
    "annual limit",
    "area of coverage",
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
    "classic plan",
    "classic 1r",
    "classic 2r",
    "classic 2",
    "classic 3",
    "classic 4",
    "hn_classic",
    "hn classic",
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