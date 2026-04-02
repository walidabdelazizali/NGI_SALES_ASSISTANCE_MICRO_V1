from __future__ import annotations

from benefit_lookup import lookup_benefit
from faq_lookup import lookup_faq
from network_lookup import lookup_network
from plan_lookup import lookup_plan
from rules_lookup import lookup_rules


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
        # "remedy 04",  # Isolated for cleanup
        # "remedy 05",  # Isolated for cleanup
    "remedy 06",
    "remedy_02",
    "remedy_03",
    "remedy_04",
    "remedy_05",
    "remedy_06",
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
    route = route_question(query)
    if route == "plan_lookup":
        return lookup_plan(query)
    if route == "benefit_lookup":
        return lookup_benefit(query)
    if route == "network_lookup":
        return lookup_network(query)
    if route == "rules_lookup":
        return lookup_rules(query)
    return lookup_faq(query)