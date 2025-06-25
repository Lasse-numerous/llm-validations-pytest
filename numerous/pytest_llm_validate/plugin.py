"""Pytest plugin for pytest-llm-validate."""

import logging
import os
import sys
from collections.abc import Callable
from typing import Any

import pytest

from .fixture import create_llm_eval_tester


def pytest_configure(config: pytest.Config) -> None:
    """Configure the pytest plugin."""
    # Configure logging for LLM evaluation results
    logger = logging.getLogger("pytest_llm_validate")
    
    # Set up logging level based on pytest verbosity or environment variable
    log_level = os.getenv("PYTEST_LLM_VALIDATE_LOG_LEVEL", "INFO").upper()
    if hasattr(config.option, 'verbose') and config.option.verbose >= 2:
        log_level = "DEBUG"
    elif hasattr(config.option, 'verbose') and config.option.verbose >= 1:
        log_level = "INFO"
    
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create console handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[LLM-VALIDATE] %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate messages
        logger.propagate = False


def pytest_unconfigure(config: pytest.Config) -> None:
    """Clean up when pytest is finished."""
    # Log a summary message
    logger = logging.getLogger("pytest_llm_validate")
    logger.info("LLM validation session completed")


@pytest.fixture
def llm_eval() -> Callable[..., Any]:
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
