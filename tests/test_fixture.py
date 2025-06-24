"""Tests for the fixture-based LLM evaluation functionality."""

from typing import Callable
from unittest.mock import Mock

import pytest

from numerous.pytest_llm_validate.fixture import LLMTester


class TestLLMEvalFixture:
    """Test class for LLM evaluation fixture functionality."""

    def test_fixture_availability(self, llm_eval: Callable[..., LLMTester]) -> None:
        """Test that llm_eval fixture is available and callable."""
        assert callable(llm_eval)

    def test_fixture_returns_tester_object(
        self, llm_eval: Callable[..., LLMTester]
    ) -> None:
        """Test that fixture returns a tester object with check method."""
        tester = llm_eval("Should return tester object")
        assert isinstance(tester, LLMTester)
        assert hasattr(tester, "check")
        assert hasattr(tester, "get_results")
        assert hasattr(tester, "get_summary")

    @pytest.fixture(autouse=True)
    def mock_get_agent(self, mocker: Mock) -> Mock:
        """Mock the get_agent function to avoid actual LLM calls."""
        from numerous.pytest_llm_validate.models import EvalResult, EvalRequest, EvalRule

        # Create a dummy rule for test results
        test_rule = EvalRule(
            name="test_rule",
            description="Test rule for mocking",
            prompt="Test prompt"
        )

        # Create a dummy request for test results
        test_request = EvalRequest(
            specification="Test specification",
            artifacts={"output": "test"},
            rule=test_rule,
            threshold=0.7,
            model="gpt-4o-mini"
        )

        mock_agent = mocker.patch("numerous.pytest_llm_validate.fixture.get_agent")
        # Mock the async evaluate method
        mock_agent.return_value.evaluate = mocker.AsyncMock()
        mock_agent.return_value.evaluate.return_value = EvalResult(
            score=0.8,
            comment="Test comment",
            passed=True,
            request=test_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )
        return mock_agent

    def test_tester_check_method_works(
        self, mock_get_agent: Mock, llm_eval: Callable[..., LLMTester]
    ) -> None:
        """Test that tester.check() method works correctly."""
        # Configure mock to return a passing result
        from numerous.pytest_llm_validate.models import EvalResult, EvalRequest, EvalRule

        test_rule = EvalRule(name="test_rule", description="Test", prompt="Test")
        test_request = EvalRequest(
            specification="Test specification",
            artifacts={"output": "test"},
            rule=test_rule
        )

        mock_agent = mock_get_agent.return_value
        mock_agent.evaluate.return_value = EvalResult(
            score=0.85,
            comment="Good output",
            passed=True,
            request=test_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )

        tester = llm_eval("Test specification", no_dedupe=True)

        # This should not raise an exception
        tester.check("test output", label="test_label")

        # Verify the agent was called
        mock_get_agent.assert_called_once()
        mock_agent.evaluate.assert_called_once()

        # Check that results are stored
        results = tester.get_results()
        assert len(results) == 1
        assert results[0].score == 0.85

    def test_multiple_checks_supported(
        self, mock_get_agent: Mock, llm_eval: Callable[..., LLMTester]
    ) -> None:
        """Test that multiple checks can be performed with the same tester."""
        # Configure mock to return passing results
        from numerous.pytest_llm_validate.models import EvalResult, EvalRequest, EvalRule

        test_rule = EvalRule(name="test_rule", description="Test", prompt="Test")
        test_request = EvalRequest(
            specification="All outputs should be professional",
            artifacts={"output": "test"},
            rule=test_rule
        )

        mock_agent = mock_get_agent.return_value
        mock_agent.evaluate.return_value = EvalResult(
            score=0.8,
            comment="Good output",
            passed=True,
            request=test_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )

        tester = llm_eval("All outputs should be professional")
        tester.check("First output", label="first")
        tester.check("Second output", label="second")

        # Verify both calls were made
        assert mock_agent.evaluate.call_count == 2

        # Check that both results are stored
        results = tester.get_results()
        assert len(results) == 2

        summary = tester.get_summary()
        assert summary["total_checks"] == 2
        assert summary["passed"] == 2

    def test_fixture_with_options(self, llm_eval: Callable[..., LLMTester]) -> None:
        """Test that fixture accepts and uses options correctly."""
        tester = llm_eval("Test with options", threshold=0.8, model="gpt-4o-mini")
        assert isinstance(tester, LLMTester)
        assert tester.specification == "Test with options"
        assert tester.threshold == 0.8
        assert tester.model == "gpt-4o-mini"

    def test_tester_check_failure(
        self, mock_get_agent: Mock, llm_eval: Callable[..., LLMTester]
    ) -> None:
        """Test that tester.check() raises AssertionError on failure."""
        # Configure mock to return a failing result
        from numerous.pytest_llm_validate.models import EvalResult, EvalRequest, EvalRule

        test_rule = EvalRule(name="test_rule", description="Test", prompt="Test")
        test_request = EvalRequest(
            specification="Should be high quality",
            artifacts={"output": "bad output"},
            rule=test_rule
        )

        mock_agent = mock_get_agent.return_value
        mock_agent.evaluate.return_value = EvalResult(
            score=0.3,
            comment="Poor quality output",
            passed=False,
            request=test_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )

        tester = llm_eval("Should be high quality")

        # This should raise an AssertionError
        with pytest.raises(AssertionError, match="LLM Evaluation Failed"):
            tester.check("bad output", label="test_label")

        # Verify the agent was called even though it failed
        mock_get_agent.assert_called_once()
        mock_agent.evaluate.assert_called_once()

        # Check that failed result is still stored
        results = tester.get_results()
        assert len(results) == 1
        assert results[0].passed is False

    def test_tester_summary_empty(self, llm_eval: Callable[..., LLMTester]) -> None:
        """Test tester summary when no checks have been performed."""
        tester = llm_eval("Test specification")
        summary = tester.get_summary()

        assert summary["total_checks"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["average_score"] == 0.0

    def test_tester_with_custom_rule(
        self, mock_get_agent: Mock, llm_eval: Callable[..., LLMTester]
    ) -> None:
        """Test tester with custom evaluation rule."""
        # Configure mock to return a passing result
        from numerous.pytest_llm_validate.models import EvalResult, EvalRequest, EvalRule

        test_rule = EvalRule(name="test_behavior", description="Test behavior", prompt="Test")
        test_request = EvalRequest(
            specification="Test with custom rule",
            artifacts={"output": "test output"},
            rule=test_rule
        )

        mock_agent = mock_get_agent.return_value
        mock_agent.evaluate.return_value = EvalResult(
            score=0.9,
            comment="Excellent behavior",
            passed=True,
            request=test_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )

        tester = llm_eval("Test with custom rule", rule="test_behavior", no_dedupe=True)
        assert tester.eval_rule.name == "test_behavior"

        tester.check("test output")

        # Verify the custom rule was used
        mock_get_agent.assert_called_once()
        call_args = mock_agent.evaluate.call_args
        eval_request = call_args[0][0]
        assert eval_request.rule.name == "test_behavior"
