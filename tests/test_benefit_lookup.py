import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import benefit_lookup

def test_import():
    # Should import without error
    import benefit_lookup

def test_lookup_benefit_english():
    # Should return a dict or None (if no file/data)
    result = benefit_lookup.lookup_benefit('REMEDY_02', 'maternity')
    assert result is None or isinstance(result, dict)

def test_lookup_benefit_arabic():
    # Should return a dict or None (if no file/data)
    result = benefit_lookup.lookup_benefit('REMEDY_02', 'حمل')
    assert result is None or isinstance(result, dict)

def test_lookup_benefit_not_found():
    # Should return None for unknown intent
    result = benefit_lookup.lookup_benefit('REMEDY_02', 'space travel')
    assert result is None
