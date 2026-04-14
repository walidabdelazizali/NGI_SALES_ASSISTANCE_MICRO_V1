"""
Phase-E hardened tests for the reconciliation-and-normalization pass.
Covers:
 1. No final mapping derived from filename alone
 2. Prime conflicts → pending_mapping (not confirmed)
 3. Path normalization works
 4. Existing staging extraction still passes
 5. Live Remedy runtime untouched

Does NOT modify any live data/src/scripts files.
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pytest

STAGING_DIR = Path(__file__).resolve().parent.parent / "staging" / "enhanced"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STAGING_DIR))

import extract_enhanced_plans as ep


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def plan_facts():
    inv = ep.build_source_inventory()
    facts, _ = ep.extract_all_tob_plans(inv)
    return facts


@pytest.fixture(scope="module")
def mapping_review_rows():
    fp = STAGING_DIR / "plan_mapping_review.csv"
    if not fp.exists():
        pytest.skip("plan_mapping_review.csv not generated yet")
    with open(fp, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def prime_reconciliation_rows():
    fp = STAGING_DIR / "prime_reconciliation.csv"
    if not fp.exists():
        pytest.skip("prime_reconciliation.csv not generated yet")
    with open(fp, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. NO FINAL MAPPING FROM FILENAME ALONE
# ═══════════════════════════════════════════════════════════════════════════════

class TestNoFilenameTruth:
    """Guarantee that plan identity is NEVER derived solely from filename."""

    def test_all_extracted_plans_use_workbook_content_identity(self, plan_facts):
        """Every high-confidence plan must have plan_identity_source == 'workbook_content'."""
        for r in plan_facts:
            if r["source_confidence"] == "high":
                assert r["plan_identity_source"] == "workbook_content", (
                    f"{r['internal_plan_code']} identity derived from "
                    f"{r['plan_identity_source']}, not workbook_content"
                )

    def test_filename_guess_is_not_canonical(self):
        """The _infer_plan_code_from_filename function exists but returns
        GUESS codes that would never match a real internal code."""
        guess = ep._infer_plan_code_from_filename("MR.HUSSEIN CLASSIC 1@.xlsx")
        assert guess is not None  # The function does return something
        assert guess.endswith("_FILENAME_GUESS"), f"Filename guess '{guess}' should end with _FILENAME_GUESS"
        # And it must NOT be a valid DISPLAY_TO_CODE value
        assert guess not in ep.DISPLAY_TO_CODE.values(), \
            f"Filename guess '{guess}' must not be a valid internal code"

    def test_filename_content_mismatch_detected(self, plan_facts):
        """Most workbooks have filename != content. Verify the flag is tracked."""
        mismatches = [r for r in plan_facts
                      if r["source_confidence"] == "high"
                      and r["filename_content_mismatch"] == "True"]
        # We know at least 5 of 6 files have misleading names
        assert len(mismatches) >= 5, (
            f"Expected >= 5 filename/content mismatches, found {len(mismatches)}"
        )

    def test_mapping_review_flags_misleading_filenames(self, mapping_review_rows):
        """plan_mapping_review.csv should note misleading filenames."""
        flagged = [r for r in mapping_review_rows if "FILENAME MISLEADING" in r.get("review_notes", "")]
        assert len(flagged) >= 5, f"Expected >= 5 misleading-filename flags, found {len(flagged)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PRIME CONFLICTS → pending_mapping, NOT confirmed
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrimeReconciliation:
    """Prime plans with network conflicts must be pending_mapping."""

    def test_prime_2_is_pending_mapping_in_reconciliation(self, prime_reconciliation_rows):
        """HN_PRIME_2 has a network conflict (HN Premier vs Standard Plus).
        It must be pending_mapping, not confirmed."""
        prime2 = [r for r in prime_reconciliation_rows if r["internal_plan_code"] == "HN_PRIME_2"]
        assert len(prime2) == 1, "HN_PRIME_2 should appear exactly once"
        assert prime2[0]["status"] == "pending_mapping", (
            f"HN_PRIME_2 status should be pending_mapping, got {prime2[0]['status']}"
        )

    def test_prime_2_is_pending_mapping_in_review(self, mapping_review_rows):
        """HN_PRIME_2 must also be pending_mapping in plan_mapping_review.csv."""
        prime2 = [r for r in mapping_review_rows if r["proposed_internal_code"] == "HN_PRIME_2"]
        assert len(prime2) == 1
        assert prime2[0]["status"] == "pending_mapping", (
            f"HN_PRIME_2 status in review should be pending_mapping, got {prime2[0]['status']}"
        )

    def test_prime_2_network_conflict_documented(self, prime_reconciliation_rows):
        """The network conflict must be explicitly documented."""
        prime2 = [r for r in prime_reconciliation_rows if r["internal_plan_code"] == "HN_PRIME_2"][0]
        assert "mismatch" in prime2["review_notes"].lower() or "conflict" in prime2["review_notes"].lower(), \
            "HN_PRIME_2 reconciliation should document the network mismatch"

    def test_prime_1_is_pending_source(self, prime_reconciliation_rows):
        """HN_PRIME_1 has no TOB workbook at all."""
        prime1 = [r for r in prime_reconciliation_rows if r["internal_plan_code"] == "HN_PRIME_1"]
        assert len(prime1) == 1
        assert prime1[0]["status"] == "pending_source"

    def test_no_prime_forced_to_confirmed(self, prime_reconciliation_rows):
        """No Prime plan should be forced to 'confirmed' status."""
        prime_rows = [r for r in prime_reconciliation_rows if r["internal_plan_code"].startswith("HN_PRIME")]
        for r in prime_rows:
            assert r["status"] != "confirmed", (
                f"{r['internal_plan_code']} is forced to confirmed — this violates reconciliation rules"
            )

    def test_classic_plans_confirmed(self, prime_reconciliation_rows):
        """Classic plans with TOB workbooks should be confirmed."""
        classics = [r for r in prime_reconciliation_rows
                    if r["internal_plan_code"].startswith("HN_CLASSIC") and r["status"] == "confirmed"]
        assert len(classics) == 5, f"Expected 5 confirmed Classic plans, found {len(classics)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PATH NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPathNormalization:
    """Verify that source files are read from the normalized structure."""

    def test_normalized_tob_dir_exists(self):
        norm = PROJECT_ROOT / "data" / "source_excel" / "enhanced_tob"
        assert norm.exists(), f"Normalized TOB dir does not exist: {norm}"

    def test_normalized_ref_dir_exists(self):
        norm = PROJECT_ROOT / "data" / "source_docs" / "enhanced_reference"
        assert norm.exists(), f"Normalized ref dir does not exist: {norm}"

    def test_normalized_tob_has_files(self):
        norm = PROJECT_ROOT / "data" / "source_excel" / "enhanced_tob"
        files = list(norm.glob("*.xlsx"))
        assert len(files) >= 6, f"Expected >= 6 xlsx files, found {len(files)}"

    def test_normalized_ref_has_pdfs(self):
        norm = PROJECT_ROOT / "data" / "source_docs" / "enhanced_reference"
        files = list(norm.glob("*.pdf"))
        assert len(files) >= 2, f"Expected >= 2 pdf files, found {len(files)}"

    def test_extraction_uses_normalized_path(self):
        """ep.TOB_DIR should resolve to the normalized path when it exists."""
        norm = PROJECT_ROOT / "data" / "source_excel" / "enhanced_tob"
        if norm.exists():
            assert ep.TOB_DIR == norm, (
                f"TOB_DIR should be {norm}, got {ep.TOB_DIR}"
            )

    def test_inventory_paths_are_normalized(self):
        inv = ep.build_source_inventory()
        tob_rows = [r for r in inv if r["source_type"] == "xlsx"]
        for r in tob_rows:
            path = r["source_path"]
            assert "datasource_excelenhanced_tob" not in path, (
                f"Inventory still using collapsed path: {path}"
            )
            assert path.startswith("data"), f"Path should start with 'data': {path}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXISTING STAGING EXTRACTION STILL WORKS
# ═══════════════════════════════════════════════════════════════════════════════

class TestStagingStillWorks:
    """Core extraction pipeline produces same quality output after refactoring."""

    def test_six_plans_still_extracted(self, plan_facts):
        high = [r for r in plan_facts if r["source_confidence"] == "high"]
        assert len(high) == 6

    def test_expected_codes_unchanged(self, plan_facts):
        codes = {r["internal_plan_code"] for r in plan_facts if r["source_confidence"] == "high"}
        expected = {"HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4", "HN_PRIME_2"}
        assert codes == expected

    def test_benefits_detail_count(self):
        inv = ep.build_source_inventory()
        _, detail = ep.extract_all_tob_plans(inv)
        assert len(detail) > 1000, f"Expected >1000 detail rows, got {len(detail)}"

    def test_pending_still_two(self, plan_facts):
        pending = ep.build_pending_plans(plan_facts)
        assert len(pending) == 2
        codes = {p["internal_plan_code"] for p in pending}
        assert codes == {"HN_PRIME_1", "HN_CLASSIC_1"}

    def test_staging_csvs_exist(self):
        """All required staging artifacts should exist."""
        required = [
            "source_inventory.csv",
            "extracted_plan_facts.csv",
            "extracted_benefits_detail.csv",
            "pending_plans.csv",
            "extraction_report.md",
            "prime_reconciliation.csv",
            "plan_mapping_review.csv",
        ]
        for fn in required:
            fp = STAGING_DIR / fn
            assert fp.exists(), f"Missing staging artifact: {fn}"
            assert fp.stat().st_size > 0, f"Empty staging artifact: {fn}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LIVE REMEDY RUNTIME UNTOUCHED
# ═══════════════════════════════════════════════════════════════════════════════

class TestLiveRuntimeUntouched:
    """Verify no live src/, data/, or scripts/ files were modified."""

    LIVE_FILES = [
        "data/plans/plan_master.csv",
        "data/benefits/outpatient_benefits.csv",
        "data/benefits/inpatient_benefits.csv",
        "data/benefits/maternity_benefits.csv",
        "data/benefits/preventive_benefits.csv",
        "data/rules/referral_rules.csv",
        "data/networks/provider_network_master.csv",
        "src/router.py",
        "src/plan_lookup.py",
        "scripts/ask_kb.py",
    ]

    def test_live_files_exist_and_nonempty(self):
        for rel in self.LIVE_FILES:
            fp = PROJECT_ROOT / rel
            if fp.exists():
                assert fp.stat().st_size > 0, f"{rel} is empty — may have been overwritten"

    def test_plan_master_has_only_remedy_and_confirmed_classic_plans(self):
        """data/plans/plan_master.csv should contain Remedy (02-06) and confirmed Classic plans only."""
        fp = PROJECT_ROOT / "data" / "plans" / "plan_master.csv"
        if not fp.exists():
            pytest.skip("plan_master.csv not found")
        CONFIRMED_CLASSICS = {"HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4"}
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row.get("plan_id", row.get("plan_code", row.get("internal_plan_code", "")))
                if pid.startswith("HN_"):
                    assert pid in CONFIRMED_CLASSICS, (
                        f"Unconfirmed enhanced plan '{pid}' found in live plan_master.csv!"
                    )
                assert "HN_PRIME" not in pid, (
                    f"Prime plan '{pid}' found in live plan_master.csv — should not be integrated!"
                )

    def test_router_has_no_prime_plan_routes(self):
        """src/router.py should NOT contain HN_PRIME routing (Classic is now live)."""
        fp = PROJECT_ROOT / "src" / "router.py"
        if not fp.exists():
            pytest.skip("router.py not found")
        text = fp.read_text(encoding="utf-8")
        assert "HN_PRIME" not in text, "router.py contains Prime plan routing — should not be integrated"

    def test_plan_lookup_has_no_prime_gates(self):
        """src/plan_lookup.py should NOT have Prime plan gates (Classic is now live)."""
        fp = PROJECT_ROOT / "src" / "plan_lookup.py"
        if not fp.exists():
            pytest.skip("plan_lookup.py not found")
        text = fp.read_text(encoding="utf-8")
        assert "HN_PRIME" not in text, "plan_lookup.py contains Prime plan references — should not be integrated"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. PLAN MAPPING REVIEW ARTIFACT COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestMappingReviewArtifact:
    """Verify plan_mapping_review.csv has all required columns and rows."""

    def test_has_required_columns(self, mapping_review_rows):
        required = [
            "source_file", "workbook_plan_name", "proposed_internal_code",
            "proposed_display_name", "workbook_network", "comparison_network",
            "annual_limit", "status", "confidence", "review_notes",
        ]
        actual = set(mapping_review_rows[0].keys()) if mapping_review_rows else set()
        for col in required:
            assert col in actual, f"Missing column: {col}"

    def test_covers_all_expected_plans(self, mapping_review_rows):
        codes = {r["proposed_internal_code"] for r in mapping_review_rows}
        for expected in ep.EXPECTED_PLAN_CODES:
            assert expected in codes, f"{expected} missing from mapping review"

    def test_statuses_are_valid(self, mapping_review_rows):
        valid = {"confirmed", "pending_mapping", "pending_source", "conflict"}
        for r in mapping_review_rows:
            assert r["status"] in valid, f"Invalid status: {r['status']}"

    def test_confidence_levels_valid(self, mapping_review_rows):
        valid = {"high", "medium", "low", "none"}
        for r in mapping_review_rows:
            assert r["confidence"] in valid, f"Invalid confidence: {r['confidence']}"
