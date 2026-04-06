from __future__ import annotations


import csv
import re
import unicodedata
from pathlib import Path

NETWORK_FILE = Path(__file__).resolve().parents[1] / "data" / "networks" / "provider_network_master.csv"
ALIAS_FILE = Path(__file__).resolve().parents[1] / "data" / "networks" / "provider_aliases.csv"

def robust_normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

_normalize = robust_normalize


def _load_providers() -> list[dict[str, str]]:
    with NETWORK_FILE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    with ALIAS_FILE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            aliases[_normalize(row["alias"])] = row["provider_name"]
    return aliases


def lookup_network(query: str) -> dict[str, str]:
    normalized_query = _normalize(query)
    providers = _load_providers()
    aliases = _load_aliases()

    # Helper to build owner-friendly answer
    def build_answer(row, direct_billing_intent=False):
        provider = row.get('provider_name')
        network = row.get('network_name')
        city = row.get('city')
        emirate = row.get('emirate')
        direct_billing = row.get('direct_billing_possible', '').strip().lower()
        if direct_billing_intent:
            if direct_billing == 'yes':
                answer = f"Direct billing is available for {provider}."
            else:
                answer = f"Direct billing is NOT available for {provider}."
            answer = f"{answer}\nPlan: {network}.\nLocation: {city}, {emirate}."
            return answer
        # Required canonical output contract for generic network
        answer = f"{provider} is in network."
        answer += f"\nPlan: {network}."
        answer += f"\nLocation: {city}, {emirate}."
        return answer

    # Direct billing intent detection (must take precedence)
    direct_billing_intent = any(x in normalized_query for x in ["direct billing", "direct", "مباشر"])

    # Try alias match (robust: substring match)
    for alias, provider_name in aliases.items():
        if alias in normalized_query:
            for row in providers:
                if _normalize(row.get("provider_name", "")) == _normalize(provider_name):
                    if direct_billing_intent:
                        return {
                            "status": "found",
                            "route": "network_lookup",
                            "provider": row.get("provider_name"),
                            "network": row.get("network_name"),
                            "answer": build_answer(row, direct_billing_intent=True)
                        }
                    return {
                        "status": "found",
                        "route": "network_lookup",
                        "provider": row.get("provider_name"),
                        "network": row.get("network_name"),
                        "answer": build_answer(row)
                    }

    # Try direct provider name match (robust: substring match)
    for row in providers:
        if _normalize(row.get("provider_name", "")) in normalized_query:
            return {
                "status": "found",
                "route": "network_lookup",
                "provider": row.get("provider_name"),
                "network": row.get("network_name"),
                "answer": build_answer(row, direct_billing_intent=direct_billing_intent),
            }

    # Try reverse partial match: if a significant query token matches start of provider name
    query_words = [w for w in normalized_query.split() if len(w) >= 4 and w.isascii()]
    for row in providers:
        pname = _normalize(row.get("provider_name", ""))
        for qw in query_words:
            if pname.startswith(qw):
                return {
                    "status": "found",
                    "route": "network_lookup",
                    "provider": row.get("provider_name"),
                    "network": row.get("network_name"),
                    "answer": build_answer(row, direct_billing_intent=direct_billing_intent),
                }

    # Try reverse partial match: if a significant query token matches start of provider name
    query_words = [w for w in normalized_query.split() if len(w) >= 4 and w.isascii()]
    for row in providers:
        pname = _normalize(row.get("provider_name", ""))
        for qw in query_words:
            if pname.startswith(qw):
                return {
                    "status": "found",
                    "route": "network_lookup",
                    "provider": row.get("provider_name"),
                    "network": row.get("network_name"),
                    "answer": build_answer(row, direct_billing_intent=direct_billing_intent),
                }

    # Try city-aware match: if query contains city or emirate
    for row in providers:
        city = _normalize(row.get('city', ''))
        emirate = _normalize(row.get('emirate', ''))
        if city and city in normalized_query:
            return {
                "status": "found",
                "route": "network_lookup",
                "provider": row.get("provider_name"),
                "network": row.get("network_name"),
                "answer": build_answer(row, direct_billing_intent=direct_billing_intent),
            }
        if emirate and emirate in normalized_query:
            return {
                "status": "found",
                "route": "network_lookup",
                "provider": row.get("provider_name"),
                "network": row.get("network_name"),
                "answer": build_answer(row, direct_billing_intent=direct_billing_intent),
            }

    return {"status": "not_found"}