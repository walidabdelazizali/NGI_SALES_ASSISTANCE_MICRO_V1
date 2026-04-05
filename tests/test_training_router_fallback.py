import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from router import dispatch_query

def test_structured_answer_priority():
    # Query that should be answered by structured plan lookup (simulate known plan field)
    result = dispatch_query('What is the annual limit for Remedy 02?')
    assert result['status'] == 'found'
    assert result['route'] != 'training_lookup'

def test_training_fallback_english():
    # Query that is benefit-intent and plan detected, but not in structured benefit table
    result = dispatch_query('Is mental health 800 per visit?')
    assert result['status'] == 'not_found'  # Deterministic: benefit intent/plan detected but not found
    assert result['route'] == 'benefit_lookup'

def test_training_fallback_arabic():
    # Query that is Arabic, but plan_lookup answers with a structured plan answer (not a fallback)
    result = dispatch_query('هل Remedy 02 فيها حمل؟')
    assert result['status'] == 'found'
    assert result['route'] == 'plan_lookup'

def test_global_supports_plan():
    # Query that is benefit-intent but not found in structured, so returns not_found
    result = dispatch_query('Is psychotherapy the same as mental health cover?')
    assert result['status'] == 'not_found'
    assert result['route'] == 'benefit_lookup'

def test_no_answer_safe():
    # Query that matches nothing, but FAQ fallback may answer
    result = dispatch_query('This is a nonsense query with no answer')
    assert result['status'] == 'found'
    assert result['route'] == 'faq_lookup'
