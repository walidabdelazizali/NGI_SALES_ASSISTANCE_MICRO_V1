from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from faq_lookup import lookup_faq


def test_lookup_faq_exact_match() -> None:
    result = lookup_faq("What is approval and why is it needed?")

    assert result["status"] == "found"
    assert result["question_id"] == "FAQ-001"
    assert "permission" in result["answer"].lower()


def test_lookup_faq_keyword_match() -> None:
    result = lookup_faq("claim processing")

    assert result["status"] == "found"
    assert result["question_id"] == "FAQ-022"
    assert "claim processing time varies" in result["answer"].lower()