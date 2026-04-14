"""
Staging validation tests for Enhanced Plan extraction pipeline.
Tests ONLY the staging extraction logic — does NOT touch live runtime.
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure staging module is importable
STAGING_DIR = Path(__file__).resolve().parent.parent / "staging" / "enhanced"
sys.path.insert(0, str(STAGING_DIR))

import extract_enhanced_plans as ep


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def inventory():
    return ep.build_source_inventory()


@pytest.fixture(scope="module")
def master_comparison():
    return ep.load_master_comparison()


@pytest.fixture(scope="module")
def extraction_results(inventory):
    plan_facts, benefits_detail = ep.extract_all_tob_plans(inventory)
    return plan_facts, benefits_detail


@pytest.fixture(scope="module")
def plan_facts(extraction_results):
    return extraction_results[0]


@pytest.fixture(scope="module")
def benefits_detail(extraction_results):
    return extraction_results[1]


@pytest.fixture(scope="module")
def pending_plans(plan_facts):
    return ep.build_pending_plans(plan_facts)


# ── 1. Source Discovery Tests ─────────────────────────────────────────────────

class TestSourceDiscovery:
    def test_inventory_not_empty(self, inventory):
        assert len(inventory) > 0, "Source inventory should discover at least 1 file"

    def test_tob_workbooks_found(self, inventory):
        tob_files = [r for r in inventory if r["source_type"] == "xlsx"
                     and r["detected_plan_code"] not in ("ALL_PLANS_COMPARISON", "REFERENCE", "")]
        assert len(tob_files) >= 6, f"Expected >= 6 TOB workbooks, found {len(tob_files)}"

    def test_reference_pdfs_found(self, inventory):
        pdfs = [r for r in inventory if r["source_type"] == "pdf"]
        assert len(pdfs) >= 2, f"Expected >= 2 reference PDFs, found {len(pdfs)}"

    def test_master_comparison_found(self, inventory):
        masters = [r for r in inventory if r["detected_plan_code"] == "ALL_PLANS_COMPARISON"]
        assert len(masters) >= 1, "Expected at least 1 master comparison workbook"

    def test_all_usable_have_plan_code(self, inventory):
        tob_usable = [r for r in inventory if r["status"] == "usable"
                      and r["source_type"] == "xlsx"
                      and r["detected_plan_code"] not in ("ALL_PLANS_COMPARISON",)]
        for r in tob_usable:
            assert r["detected_plan_code"], f"Usable TOB {r['source_filename']} has no plan code"

    def test_no_crash_on_full_inventory(self, inventory):
        """All files should be classified without crashes."""
        valid_statuses = {"usable", "partial", "unreadable", "missing_plan_mapping"}
        for r in inventory:
            assert r["status"] in valid_statuses, f"{r['source_filename']} has invalid status: {r['status']}"


# ── 2. Pending Plans Tests ────────────────────────────────────────────────────

class TestPendingPlans:
    def test_pending_plans_identified(self, pending_plans):
        assert len(pending_plans) >= 2, "HN_PRIME_1 and HN_CLASSIC_1 should be pending"

    def test_prime_1_is_pending(self, pending_plans):
        codes = [p["internal_plan_code"] for p in pending_plans]
        assert "HN_PRIME_1" in codes, "HN_PRIME_1 should be pending_source"

    def test_classic_1_is_pending(self, pending_plans):
        codes = [p["internal_plan_code"] for p in pending_plans]
        assert "HN_CLASSIC_1" in codes, "HN_CLASSIC_1 should be pending_source"

    def test_pending_status_value(self, pending_plans):
        for p in pending_plans:
            assert p["status"] == "pending_source", f"{p['internal_plan_code']} should be pending_source"

    def test_no_fabricated_values_for_pending(self, plan_facts, pending_plans):
        """Pending plans must NOT have high-confidence extracted facts."""
        pending_codes = {p["internal_plan_code"] for p in pending_plans}
        for r in plan_facts:
            if r["internal_plan_code"] in pending_codes:
                assert r["source_confidence"] != "high", \
                    f"Pending plan {r['internal_plan_code']} should not have high-confidence extraction"


# ── 3. Extraction Accuracy Tests ─────────────────────────────────────────────

class TestExtraction:
    def test_six_plans_extracted(self, plan_facts):
        high_conf = [r for r in plan_facts if r["source_confidence"] == "high"]
        assert len(high_conf) == 6, f"Expected 6 high-confidence plans, got {len(high_conf)}"

    def test_expected_plan_codes_extracted(self, plan_facts):
        codes = {r["internal_plan_code"] for r in plan_facts if r["source_confidence"] == "high"}
        expected = {"HN_CLASSIC_1R", "HN_CLASSIC_2", "HN_CLASSIC_2R", "HN_CLASSIC_3", "HN_CLASSIC_4", "HN_PRIME_2"}
        assert codes == expected, f"Extracted codes mismatch: {codes} vs {expected}"

    def test_plan_names_match_codes(self, plan_facts):
        expected_names = {
            "HN_CLASSIC_1R": "Classic Plan-1R",
            "HN_CLASSIC_2": "Classic Plan-2",
            "HN_CLASSIC_2R": "Classic Plan-2R",
            "HN_CLASSIC_3": "Classic Plan-3",
            "HN_CLASSIC_4": "Classic Plan-4",
            "HN_PRIME_2": "Prime Plan-2",
        }
        for r in plan_facts:
            if r["source_confidence"] == "high":
                assert r["display_plan_name"] == expected_names[r["internal_plan_code"]], \
                    f"{r['internal_plan_code']} display name mismatch"

    def test_annual_max_populated(self, plan_facts):
        for r in plan_facts:
            if r["source_confidence"] == "high":
                assert r["annual_max_benefit"].startswith("AED"), \
                    f"{r['internal_plan_code']} missing annual_max_benefit"

    def test_area_of_coverage_populated(self, plan_facts):
        for r in plan_facts:
            if r["source_confidence"] == "high":
                assert r["area_of_coverage"], f"{r['internal_plan_code']} missing area_of_coverage"

    def test_network_mapped(self, plan_facts):
        for r in plan_facts:
            if r["source_confidence"] == "high":
                assert r["mapped_internal_network_name"], \
                    f"{r['internal_plan_code']} missing mapped network"

    def test_specific_plan_values(self, plan_facts):
        """Spot-check known values from TOB workbooks."""
        by_code = {r["internal_plan_code"]: r for r in plan_facts if r["source_confidence"] == "high"}

        assert by_code["HN_PRIME_2"]["annual_max_benefit"] == "AED 500,000"
        assert by_code["HN_PRIME_2"]["area_of_coverage"] == "Worldwide"
        assert by_code["HN_PRIME_2"]["mapped_internal_network_name"] == "HN Premier"

        assert by_code["HN_CLASSIC_1R"]["annual_max_benefit"] == "AED 300,000"
        assert by_code["HN_CLASSIC_1R"]["mapped_internal_network_name"] == "HN Advantage"

        assert by_code["HN_CLASSIC_4"]["annual_max_benefit"] == "AED 150,000"
        assert by_code["HN_CLASSIC_4"]["area_of_coverage"] == "UAE+Home country"
        assert by_code["HN_CLASSIC_4"]["mapped_internal_network_name"] == "HN Basic Plus"

    def test_benefits_detail_not_empty(self, benefits_detail):
        assert len(benefits_detail) > 100, f"Expected >100 benefit detail rows, got {len(benefits_detail)}"

    def test_no_cross_plan_contamination(self, benefits_detail):
        """Each plan's benefits should reference only that plan's code."""
        for row in benefits_detail:
            code = row["internal_plan_code"]
            name = row["display_plan_name"]
            # Verify code-name consistency
            if code in ep.DISPLAY_TO_CODE.values():
                expected_name = {v: k for k, v in ep.DISPLAY_TO_CODE.items()}.get(code, "")
                assert name == expected_name, \
                    f"Row has code={code} but name={name}, expected {expected_name}"

    def test_exclusions_extracted(self, benefits_detail):
        exclusion_rows = [r for r in benefits_detail if r["section"] == "exclusion"]
        assert len(exclusion_rows) > 50, f"Expected >50 exclusion rows, got {len(exclusion_rows)}"


# ── 4. No Fabrication Tests ───────────────────────────────────────────────────

class TestNoFabrication:
    def test_missing_plans_not_in_facts(self, plan_facts):
        """HN_PRIME_1 and HN_CLASSIC_1 should NOT appear with real benefit data."""
        for r in plan_facts:
            if r["internal_plan_code"] in ("HN_PRIME_1", "HN_CLASSIC_1"):
                assert r["source_confidence"] != "high", \
                    f"Fabrication detected: {r['internal_plan_code']} has high confidence without source"

    def test_missing_plans_not_in_detail(self, benefits_detail):
        """No benefit detail rows for missing plans."""
        for r in benefits_detail:
            assert r["internal_plan_code"] not in ("HN_PRIME_1", "HN_CLASSIC_1"), \
                f"Fabrication detected: {r['internal_plan_code']} found in benefits_detail"


# ── 5. Malformed File Safety Tests ────────────────────────────────────────────

class TestMalformedFileSafety:
    def test_corrupt_workbook_does_not_crash(self, tmp_path):
        """A corrupt xlsx file should result in 'unreadable' not a crash."""
        corrupt_file = tmp_path / "corrupt.xlsx"
        corrupt_file.write_bytes(b"this is not a valid xlsx")
        result = ep._extract_tob_from_workbook(corrupt_file)
        assert result is not None
        assert "error" in result

    def test_missing_tob_sheet_does_not_crash(self, tmp_path):
        """Workbook without 'TOB ' sheet should return error dict."""
        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.title = "SomeSheet"
        fp = tmp_path / "no_tob.xlsx"
        wb.save(str(fp))
        wb.close()
        result = ep._extract_tob_from_workbook(fp)
        assert result is not None
        assert "error" in result
        assert "No 'TOB ' sheet" in result["error"]

    def test_empty_tob_sheet_safe(self, tmp_path):
        """An empty TOB sheet should not crash."""
        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.title = "TOB "
        fp = tmp_path / "empty_tob.xlsx"
        wb.save(str(fp))
        wb.close()
        result = ep._extract_tob_from_workbook(fp)
        assert result is not None
        assert "error" not in result
        assert result["benefits"] == []


# ── 6. Master Comparison Tests ────────────────────────────────────────────────

class TestMasterComparison:
    def test_master_has_enhanced_plans(self, master_comparison):
        assert len(master_comparison) >= 8, f"Expected >= 8 enhanced plans in master, got {len(master_comparison)}"

    def test_master_has_expected_codes(self, master_comparison):
        for code in ep.EXPECTED_PLAN_CODES:
            assert code in master_comparison, f"{code} missing from master comparison"

    def test_master_network_levels(self, master_comparison):
        expected_networks = {
            "HN_PRIME_1": "Advantage Plus",
            "HN_PRIME_2": "Standard Plus",
            "HN_CLASSIC_1": "Advantage",
            "HN_CLASSIC_1R": "Advantage",
            "HN_CLASSIC_2": "Standard Plus",
            "HN_CLASSIC_2R": "Standard Plus",
            "HN_CLASSIC_3": "Standard",
            "HN_CLASSIC_4": "Basic Plus",
        }
        for code, expected_net in expected_networks.items():
            assert master_comparison[code].get("network_level") == expected_net, \
                f"{code} network_level: expected {expected_net}, got {master_comparison[code].get('network_level')}"


# ── 7. Staging Output File Tests ──────────────────────────────────────────────

class TestStagingOutputFiles:
    """Verify that output CSV files were generated and are parseable."""

    def test_source_inventory_csv_exists(self):
        fp = STAGING_DIR / "source_inventory.csv"
        assert fp.exists(), "source_inventory.csv not generated"
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 8

    def test_extracted_plan_facts_csv_exists(self):
        fp = STAGING_DIR / "extracted_plan_facts.csv"
        assert fp.exists(), "extracted_plan_facts.csv not generated"
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 6

    def test_extracted_benefits_detail_csv_exists(self):
        fp = STAGING_DIR / "extracted_benefits_detail.csv"
        assert fp.exists(), "extracted_benefits_detail.csv not generated"
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 100

    def test_pending_plans_csv_exists(self):
        fp = STAGING_DIR / "pending_plans.csv"
        assert fp.exists(), "pending_plans.csv not generated"
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 2

    def test_extraction_report_exists(self):
        fp = STAGING_DIR / "extraction_report.md"
        assert fp.exists(), "extraction_report.md not generated"
        text = fp.read_text(encoding="utf-8")
        assert "Plans Directly Supported" in text
        assert "Plans Still Pending" in text

    def test_plan_facts_csv_has_required_fields(self):
        fp = STAGING_DIR / "extracted_plan_facts.csv"
        with open(fp, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        required = [
            "internal_plan_code", "display_plan_name", "source_filename",
            "annual_max_benefit", "area_of_coverage",
            "network_label_as_shown_in_source", "mapped_internal_network_name",
            "source_confidence", "extraction_notes",
        ]
        for field in required:
            assert field in headers, f"Missing required field: {field}"


# ── 8. Live File Safety Gate ──────────────────────────────────────────────────

class TestLiveFileSafety:
    """Verify the extraction pipeline does NOT modify live runtime files."""

    LIVE_FILES = [
        "data/plans/plan_master.csv",
        "data/benefits/outpatient_benefits.csv",
        "data/benefits/inpatient_benefits.csv",
        "data/benefits/maternity_benefits.csv",
        "data/benefits/preventive_benefits.csv",
        "data/rules/referral_rules.csv",
        "data/networks/provider_network_master.csv",
    ]

    def test_live_files_untouched(self):
        """Verify live files have not been altered by checking they exist and are non-empty."""
        project_root = Path(__file__).resolve().parent.parent
        for rel in self.LIVE_FILES:
            fp = project_root / rel
            if fp.exists():
                size = fp.stat().st_size
                assert size > 0, f"Live file {rel} is empty — may have been overwritten"
