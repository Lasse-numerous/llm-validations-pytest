"""Pytest plugin for pytest-llm-validate."""

import pytest

from .fixture import create_llm_eval_tester


@pytest.fixture
def llm_eval():
    """Pytest fixture for LLM-based evaluation.
    
    This fixture returns a factory function that creates Tester objects
    for performing multiple LLM evaluations within a single test.
    
    Returns:
        Function that creates Tester instances
        
    Example:
        def test_multiple_outputs(llm_eval):
            tester = llm_eval("All outputs should be professional and helpful")
            
            result1 = generate_email_response("complaint")
            tester.check(result1, label="complaint_response")
            
            result2 = generate_email_response("inquiry") 
            tester.check(result2, label="inquiry_response")
    """
    return create_llm_eval_tester