"""Working tests for fixture.py module coverage."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

# Force execution of import lines by importing the module directly
import numerous.pytest_llm_validate.fixture as fixture_module
from numerous.pytest_llm_validate.fixture import LLMTester, create_llm_eval_tester
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


def test_import_statements_execution() -> None:
    """Test that import statements in fixture.py are executed (lines 3-19)."""
    # Force execution of import statements by accessing imported symbols

    # Line 3: import asyncio
    assert hasattr(fixture_module, "asyncio")
    assert fixture_module.asyncio is asyncio

    # Line 4: import logging
    assert hasattr(fixture_module, "logging")

    # Line 5: from typing import Any
    assert hasattr(fixture_module, "Any")

    # Line 7: from .agent import get_agent
    assert hasattr(fixture_module, "get_agent")

    # Line 8: from .history import get_history
    assert hasattr(fixture_module, "get_history")

    # Line 9: from .loader import get_default_rule, get_rule
    assert hasattr(fixture_module, "get_default_rule")
    assert hasattr(fixture_module, "get_rule")

    # Line 10: from .models import EvalRequest, EvalResult
    assert hasattr(fixture_module, "EvalRequest")
    assert hasattr(fixture_module, "EvalResult")

    # Line 12-13: Configure logger for LLM evaluation results
    assert hasattr(fixture_module, "logger")
    assert isinstance(fixture_module.logger, logging.Logger)


def test_llm_tester_class_definition() -> None:
    """Test LLMTester class definition and initialization."""
    # Test class docstring (around line 19)
    assert LLMTester.__doc__ is not None
    assert "Tester object for performing multiple LLM evaluations" in LLMTester.__doc__

    # Test that class can be instantiated
    tester = LLMTester("Test specification")
    assert isinstance(tester, LLMTester)


def test_llm_tester_init_with_rule_parameter() -> None:
    """Test LLMTester initialization with rule parameter (covers lines around 56)."""
    with patch("numerous.pytest_llm_validate.fixture.get_rule") as mock_get_rule:
        with patch(
            "numerous.pytest_llm_validate.fixture.get_default_rule"
        ) as mock_get_default:
            mock_rule = EvalRule(name="test", description="test", prompt="test")
            mock_get_rule.return_value = mock_rule
            mock_get_default.return_value = mock_rule

                        # Test with explicit rule (line 56: if rule is not None)
            tester = LLMTester("Test spec", rule="custom_rule")
            assert tester.rule_name == "custom_rule"
            
            # Should call get_rule with the provided rule name
            mock_get_rule.assert_called_with("custom_rule")


def test_llm_tester_init_without_rule_parameter() -> None:
    """Test LLMTester initialization without rule parameter (covers default rule path)."""
    with patch("numerous.pytest_llm_validate.fixture.get_rule") as mock_get_rule:
        with patch(
            "numerous.pytest_llm_validate.fixture.get_default_rule"
        ) as mock_get_default:
            mock_rule = EvalRule(name="default", description="test", prompt="test")
            mock_get_rule.return_value = None  # Rule not found
            mock_get_default.return_value = mock_rule

                        # Test without explicit rule (should use default)
            tester = LLMTester("Test spec")
            assert tester.specification == "Test spec"
            
            # Should get default rule since rule is None
            mock_get_default.assert_called()


def test_check_method_label_artifacts() -> None:
    """Test check method with label to cover artifact creation logic (lines around 81)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        with patch("numerous.pytest_llm_validate.fixture.get_agent") as mock_get_agent:
            with patch(
                "numerous.pytest_llm_validate.fixture.get_history"
            ) as mock_get_history:
                mock_rule = EvalRule(name="test", description="test", prompt="test")
                mock_get_default.return_value = mock_rule

                # Mock the history to return no cached result
                mock_history = MagicMock()
                mock_history.get_cached_result.return_value = None
                mock_get_history.return_value = mock_history

                # Create a proper EvalRequest and EvalResult for mocking
                mock_request = EvalRequest(
                    specification="test", artifacts={"code": "test"}, rule=mock_rule
                )
                mock_result = EvalResult(
                    score=0.8,
                    comment="test",
                    passed=True,
                    request=mock_request,
                    model_used="test",
                    timestamp="2024-01-01T00:00:00",
                )

                # Mock the agent evaluation
                mock_agent = AsyncMock()
                mock_agent.evaluate.return_value = mock_result
                mock_get_agent.return_value = mock_agent

                tester = LLMTester("Test spec")

                # Test with label (line 81: if label:)
                tester.check("test output", label="test_label")

                # Verify artifacts were created properly
                assert len(tester.checks) == 1
                check = tester.checks[0]
                assert check["label"] == "test_label"
                assert "output" in check["artifacts"]


def test_check_method_no_dedupe_true() -> None:
    """Test check method with no_dedupe=True (covers lines around 117-119)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        with patch("numerous.pytest_llm_validate.fixture.get_agent") as mock_get_agent:
            with patch(
                "numerous.pytest_llm_validate.fixture.get_history"
            ) as mock_get_history:
                mock_rule = EvalRule(name="test", description="test", prompt="test")
                mock_get_default.return_value = mock_rule

                # Mock the history
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                # Create proper request and result
                mock_request = EvalRequest(
                    specification="test", artifacts={"code": "test"}, rule=mock_rule
                )
                mock_result = EvalResult(
                    score=0.8,
                    comment="test",
                    passed=True,
                    request=mock_request,
                    model_used="test",
                    timestamp="2024-01-01T00:00:00",
                )

                mock_agent = AsyncMock()
                mock_agent.evaluate.return_value = mock_result
                mock_get_agent.return_value = mock_agent

                # Test with no_dedupe=True (default)
                tester = LLMTester("Test spec", no_dedupe=True)
                tester.check("test output")

                # Should not call get_cached_result because no_dedupe=True
                mock_history.get_cached_result.assert_not_called()


def test_get_results_method() -> None:
    """Test get_results method (covers lines around 194)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        mock_rule = EvalRule(name="test", description="test", prompt="test")
        mock_get_default.return_value = mock_rule

        tester = LLMTester("Test spec")

        # Initially should be empty
        results = tester.get_results()
        assert isinstance(results, list)
        assert len(results) == 0

        # Test that it returns a copy
        assert results is not tester.results


def test_get_summary_method_with_empty_results() -> None:
    """Test get_summary method with no results (covers summary calculation lines)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        mock_rule = EvalRule(name="test", description="test", prompt="test")
        mock_get_default.return_value = mock_rule

        tester = LLMTester("Test spec")

        # Test empty summary
        summary = tester.get_summary()

        # Test summary structure for empty case
        assert summary["total_checks"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["average_score"] == 0.0
        assert summary["checks"] == []


def test_log_summary_method() -> None:
    """Test log_summary method (covers remaining lines)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        mock_rule = EvalRule(name="test", description="test", prompt="test")
        mock_get_default.return_value = mock_rule

        tester = LLMTester("Test spec")

        with patch.object(fixture_module.logger, "info") as mock_log_info:
            # Test with no results
            tester.log_summary()

            # Should log summary
            assert mock_log_info.call_count >= 1

            # Verify the summary logging content
            logged_calls = [call.args[0] for call in mock_log_info.call_args_list]
            summary_logged = any(
                "LLM Evaluation Summary" in call for call in logged_calls
            )
            assert summary_logged


def test_create_llm_eval_tester_function() -> None:
    """Test create_llm_eval_tester function definition and execution."""
    # Test function exists and is callable
    assert callable(create_llm_eval_tester)

    # Test function docstring
    assert create_llm_eval_tester.__doc__ is not None
    assert (
        "Create a new Tester instance for LLM evaluation"
        in create_llm_eval_tester.__doc__
    )

    # Test function creates LLMTester instance
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        mock_rule = EvalRule(name="test", description="test", prompt="test")
        mock_get_default.return_value = mock_rule

        tester = create_llm_eval_tester("Test specification")
        assert isinstance(tester, LLMTester)
        assert tester.specification == "Test specification"


def test_check_method_metadata_combination() -> None:
    """Test check method metadata combination logic (covers lines around 108)."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        with patch("numerous.pytest_llm_validate.fixture.get_agent") as mock_get_agent:
            with patch(
                "numerous.pytest_llm_validate.fixture.get_history"
            ) as mock_get_history:
                mock_rule = EvalRule(name="test", description="test", prompt="test")
                mock_get_default.return_value = mock_rule

                # Mock the history
                mock_history = MagicMock()
                mock_history.get_cached_result.return_value = None
                mock_get_history.return_value = mock_history

                # Create proper request and result
                mock_request = EvalRequest(
                    specification="test", artifacts={"code": "test"}, rule=mock_rule
                )
                mock_result = EvalResult(
                    score=0.8,
                    comment="test",
                    passed=True,
                    request=mock_request,
                    model_used="test",
                    timestamp="2024-01-01T00:00:00",
                )

                mock_agent = AsyncMock()
                mock_agent.evaluate.return_value = mock_result
                mock_get_agent.return_value = mock_agent

                # Test with global metadata and check-specific metadata
                tester = LLMTester("Test spec", metadata={"global": "value"})
                tester.check("test output", check_specific="data")

                # Verify check was recorded
                assert len(tester.checks) == 1
                check = tester.checks[0]
                assert "metadata" in check
                assert check["metadata"]["check_specific"] == "data"


def test_llm_tester_initialization_fields() -> None:
    """Test LLMTester initialization with all fields to cover __init__ lines."""
    with patch(
        "numerous.pytest_llm_validate.fixture.get_default_rule"
    ) as mock_get_default:
        mock_rule = EvalRule(name="test", description="test", prompt="test")
        mock_get_default.return_value = mock_rule

        # Test initialization with all parameters
        tester = LLMTester(
            "Test specification",
            threshold=0.9,
            model="gpt-4",
            rule="custom_rule",
            no_dedupe=False,
            custom_metadata="value",
        )

        # Verify all fields are set correctly
        assert tester.specification == "Test specification"
        assert tester.threshold == 0.9
        assert tester.model == "gpt-4"
        assert tester.rule_name == "custom_rule"
        assert tester.no_dedupe is False
        assert "custom_metadata" in tester.metadata
        assert tester.metadata["custom_metadata"] == "value"

        # Verify containers are initialized
        assert isinstance(tester.checks, list)
        assert isinstance(tester.results, list)
        assert len(tester.checks) == 0
        assert len(tester.results) == 0
