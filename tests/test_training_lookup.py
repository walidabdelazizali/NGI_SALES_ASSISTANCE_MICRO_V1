import pytest
import os
import sys
import importlib.util

# Ensure src/ is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import training_lookup


def test_loads_successfully():
    records = training_lookup.load_training_records()
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    assert len(records) > 0

def test_arabic_and_english_records():
    records = training_lookup.load_training_records()
    langs = set(r['lang'] for r in records)
    assert 'en' in langs
    assert 'ar' in langs

def test_plan_filter():
    remedy_records = training_lookup.get_training_records_for_plan('REMEDY_02')
    assert all(r['plan_id'] == 'REMEDY_02' or r['plan_id'] == 'GLOBAL' for r in remedy_records)
    # Should include at least one plan-specific and one GLOBAL
    assert any(r['plan_id'] == 'REMEDY_02' for r in remedy_records)
    assert any(r['plan_id'] == 'GLOBAL' for r in remedy_records)

def test_category_filter():
    benefit_records = training_lookup.search_training_records('', category='benefit')
    assert all(r['category'] == 'benefit' for r in benefit_records)
    assert len(benefit_records) > 0

def test_keyword_and_question_search():
    # English keyword
    results = training_lookup.search_training_records('maternity')
    assert any('maternity' in r['question'].lower() or any('maternity' in k for k in r['keywords']) for r in results)
    # Arabic keyword
    results_ar = training_lookup.search_training_records('حمل')
    assert any('حمل' in r['question'] or any('حمل' in k for k in r['keywords']) for r in results_ar)

def test_global_inclusion():
    # Should include both REMEDY_02 and GLOBAL records for a matching query
    records = training_lookup.search_training_records('network', plan_id='REMEDY_02')
    assert any(r['plan_id'] == 'GLOBAL' for r in records)
    assert any(r['plan_id'] == 'REMEDY_02' for r in records)
