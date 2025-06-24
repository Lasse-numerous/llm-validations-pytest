"""Tests for the @llm_eval decorator functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from numerous.pytest_llm_validate import llm_eval
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult


class TestLLMEvalDecorator:
    """Test cases for @llm_eval decorator functionality."""

    def test_decorator_import_exists(self) -> None:
        """Test that llm_eval decorator can be imported."""
        assert llm_eval is not None
        assert callable(llm_eval)

    @patch("numerous.pytest_llm_validate.decorator.get_agent")
    def test_decorator_captures_return_value(self, mock_get_agent: Mock) -> None:
        """Test that decorator captures test function return value."""
        # Create a valid EvalRequest for the mock result
        from numerous.pytest_llm_validate.loader import get_default_rule

        mock_request = EvalRequest(
            specification="test spec",
            artifacts={"return_value": "test"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini",
        )

        # Mock the agent evaluation
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.8,
            comment="Good output",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent

        @llm_eval("Should capture this return value")
        def test_return_capture() -> dict[str, str]:
            return {"message": "test output"}

        # Should not raise an exception since evaluation passes
        result = test_return_capture()
        assert result == {"message": "test output"}

        # Verify the agent was called with proper artifacts
        mock_agent.evaluate.assert_called_once()
        call_args = mock_agent.evaluate.call_args[0][0]  # Get the EvalRequest
        assert isinstance(call_args, EvalRequest)
        assert call_args.specification == "Should capture this return value"
        assert "return_value" in call_args.artifacts
        assert call_args.artifacts["return_value"] == {"message": "test output"}

    @patch("numerous.pytest_llm_validate.decorator.get_agent")
    def test_decorator_captures_stdout(self, mock_get_agent: Mock) -> None:
        """Test that decorator captures stdout from test execution."""
        # Create a valid EvalRequest for the mock result
        from numerous.pytest_llm_validate.loader import get_default_rule

        mock_request = EvalRequest(
            specification="test spec",
            artifacts={"return_value": "test", "stdout": "output"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini",
        )

        # Mock the agent evaluation
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.9,
            comment="Good output with print",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent

        @llm_eval("Should capture printed output")
        def test_stdout_capture() -> str:
            print("This should be captured")
            return "test result"

        result = test_stdout_capture()
        assert result == "test result"

        # Verify stdout was captured
        call_args = mock_agent.evaluate.call_args[0][0]
        assert "stdout" in call_args.artifacts
        assert call_args.artifacts["stdout"] == "This should be captured\n"

    @patch("numerous.pytest_llm_validate.decorator.get_agent")
    def test_decorator_evaluation_failure(self, mock_get_agent: Mock) -> None:
        """Test that decorator raises AssertionError when evaluation fails."""
        # Create a valid EvalRequest for the mock result
        from numerous.pytest_llm_validate.loader import get_default_rule

        mock_request = EvalRequest(
            specification="Should be high quality",
            artifacts={"return_value": "bad output"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini",
        )

        # Mock the agent evaluation to fail
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.3,  # Below default threshold of 0.7
            comment="Poor quality output",
            passed=False,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent

        @llm_eval("Should be high quality")
        def test_failing_evaluation() -> str:
            return "bad output"

        # Should raise AssertionError with detailed message
        with pytest.raises(AssertionError) as exc_info:
            test_failing_evaluation()

        error_msg = str(exc_info.value)
        assert "LLM Evaluation Failed" in error_msg
        assert "score: 0.30" in error_msg
        assert "threshold: 0.70" in error_msg
        assert "Should be high quality" in error_msg
        assert "Poor quality output" in error_msg

    @patch("numerous.pytest_llm_validate.decorator.get_agent")
    def test_decorator_with_custom_threshold(self, mock_get_agent: Mock) -> None:
        """Test that decorator respects custom threshold parameter."""
        # Create a valid EvalRequest for the mock result
        from numerous.pytest_llm_validate.loader import get_default_rule

        mock_request = EvalRequest(
            specification="Test with custom threshold",
            artifacts={"return_value": "moderate output"},
            rule=get_default_rule(),
            threshold=0.5,
            model="gpt-4o-mini",
        )

        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.6,
            comment="Moderate quality",
            passed=True,  # Should pass with custom threshold
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent

        @llm_eval("Test with custom threshold", threshold=0.5, no_dedupe=True)
        def test_custom_threshold() -> str:
            return "moderate output"

        # Should pass since 0.6 >= 0.5
        result = test_custom_threshold()
        assert result == "moderate output"

        # Verify threshold was passed correctly
        call_args = mock_agent.evaluate.call_args[0][0]
        assert call_args.threshold == 0.5

    @patch("numerous.pytest_llm_validate.decorator.get_agent")
    def test_decorator_captures_exceptions(self, mock_get_agent: Mock) -> None:
        """Test that decorator captures exceptions from test functions."""
        # Create a valid EvalRequest for the mock result
        from numerous.pytest_llm_validate.loader import get_default_rule

        mock_request = EvalRequest(
            specification="Should handle exceptions gracefully",
            artifacts={"return_value": "Exception: ValueError: Test exception"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini",
        )

        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.8,
            comment="Exception handled appropriately",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent

        @llm_eval("Should handle exceptions gracefully", no_dedupe=True)
        def test_exception_handling() -> None:
            raise ValueError("Test exception")

        # Should not re-raise the ValueError, but capture it for evaluation
        result = test_exception_handling()
        assert "Exception: ValueError: Test exception" in str(result)

        # Verify exception was captured in artifacts
        call_args = mock_agent.evaluate.call_args[0][0]
        assert "Exception: ValueError: Test exception" in str(
            call_args.artifacts["return_value"]
        )
