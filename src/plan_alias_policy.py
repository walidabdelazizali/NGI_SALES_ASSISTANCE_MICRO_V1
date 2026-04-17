"""
Centralized plan alias policy — single source of truth.

Every plan name resolution in the system MUST go through resolve_plan_alias().
This prevents:
  - Unconfirmed names silently mapping to nearby plans
  - Classic 1 accidentally resolving to Classic 1R
  - Prime names falling back to Remedy
  - Scattered duplicate regex/set definitions
"""
import re

# ── Canonical plan IDs ──
# Only plan IDs listed here are valid at runtime.

CONFIRMED_REMEDY_IDS = frozenset({
    "REMEDY_02", "REMEDY_03", "REMEDY_04", "REMEDY_05", "REMEDY_06",
})

CONFIRMED_CLASSIC_IDS = frozenset({
    "HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4",
})

# Explicitly excluded — these names are recognized but intentionally blocked.
# They must NEVER silently resolve to another plan.
EXCLUDED_PLAN_PATTERNS = {
    "HN_CLASSIC_1",   # No TOB workbook — insufficient evidence
    "HN_PRIME_1",     # No source data
    "HN_PRIME_2",     # Network conflict between sources
}

ALL_CONFIRMED_IDS = CONFIRMED_REMEDY_IDS | CONFIRMED_CLASSIC_IDS

# ── Deployment scope ──
# Controls which confirmed plans are approved for production answers.
# Plans outside this set return safe fallback even if data exists.
# Expand this set only after answer-quality validation for the new plan.
DEPLOYMENT_APPROVED_PLANS: frozenset[str] = frozenset({
    "REMEDY_02", "REMEDY_03", "REMEDY_04", "REMEDY_05", "REMEDY_06",
    "HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4",
})

# ── Alias table ──
# Maps normalized lowercase alias → canonical plan_id.
# Only confirmed, verified mappings are listed.

_ALIAS_TABLE: dict[str, str] = {}

def _build_alias_table() -> dict[str, str]:
    """Build alias table from confirmed plans. Called once at import."""
    t: dict[str, str] = {}

    # Remedy aliases
    for num in ("02", "03", "04", "05", "06"):
        pid = f"REMEDY_{num}"
        for prefix in ("remedy", "ريمدي", "ريميدي"):
            t[f"{prefix} {num}"] = pid
            t[f"{prefix}{num}"] = pid
            t[f"{prefix}_{num}"] = pid
            t[f"{prefix}-{num}"] = pid

    # Classic aliases — strict: only confirmed suffixes
    _classic_suffixes = {
        "1r": "HN_CLASSIC_1R",
        "2":  "HN_CLASSIC_2",
        "2r": "HN_CLASSIC_2R",
        "3":  "HN_CLASSIC_3",
        "4":  "HN_CLASSIC_4",
    }
    for suffix, pid in _classic_suffixes.items():
        for prefix in ("classic", "hn classic", "hn_classic", "كلاسيك"):
            t[f"{prefix} {suffix}"] = pid
            t[f"{prefix}_{suffix}"] = pid
            t[f"{prefix}-{suffix}"] = pid
            # "classic plan" variant
            t[f"{prefix} plan {suffix}"] = pid
            t[f"{prefix} plan-{suffix}"] = pid

    return t

_ALIAS_TABLE = _build_alias_table()


# ── Regex patterns for plan family detection ──
# These are used to detect whether a query mentions a specific plan family,
# even if the exact alias isn't in the table (e.g. for blocking excluded names).

CLASSIC_PLAN_RE = re.compile(
    r'(?:hn[_\s]?)?(?:classic|كلاسيك)[_\s]*(?:plan[_\s-]*)?(1r|2r|1|2|3|4)\b',
    re.IGNORECASE,
)

PRIME_PLAN_RE = re.compile(
    r'(?:hn[_\s]?)?(?:prime|برايم)[_\s]*(?:plan[_\s-]*)?(1|2)\b',
    re.IGNORECASE,
)

REMEDY_PLAN_RE = re.compile(
    r'(?:remedy|ريمدي|ريميدي)[_\s-]*(\d{2,})',
    re.IGNORECASE,
)


def resolve_plan_alias(normalized_query: str) -> tuple[str | None, str]:
    """
    Resolve a query to a canonical plan_id.

    Returns:
        (plan_id, status) where status is one of:
        - "confirmed"  — plan_id is a confirmed plan, safe to answer
        - "excluded"   — plan was recognized but is intentionally blocked
        - "unknown"    — no plan family detected in query
        - "unrecognized_remedy" — Remedy number not in confirmed set
    """
    q = normalized_query.lower()

    # 1. Check Classic family first (more specific match)
    cm = CLASSIC_PLAN_RE.search(q)
    if cm:
        suffix = cm.group(1).upper()
        candidate = f"HN_CLASSIC_{suffix}"
        if candidate in CONFIRMED_CLASSIC_IDS:
            return candidate, "confirmed"
        if candidate in EXCLUDED_PLAN_PATTERNS:
            return candidate, "excluded"
        return candidate, "excluded"  # Any unrecognized Classic is excluded

    # 2. Check Prime family — all excluded
    pm = PRIME_PLAN_RE.search(q)
    if pm:
        suffix = pm.group(1)
        candidate = f"HN_PRIME_{suffix}"
        return candidate, "excluded"

    # 3. Check Remedy family
    rm = REMEDY_PLAN_RE.search(q)
    if rm:
        num = rm.group(1)
        candidate = f"REMEDY_{num}"
        if candidate in CONFIRMED_REMEDY_IDS:
            return candidate, "confirmed"
        return candidate, "unrecognized_remedy"

    return None, "unknown"
