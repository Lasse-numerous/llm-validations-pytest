"""Tests for the llm_eval fixture functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from numerous.pytest_llm_validate.models import EvalResult, EvalRequest
from numerous.pytest_llm_validate.fixture import Tester


class TestLLMEvalFixture:
    """Test cases for llm_eval fixture functionality."""

    def test_fixture_availability(self, llm_eval) -> None:
        """Test that llm_eval fixture is available."""
        assert llm_eval is not None
        assert callable(llm_eval)

    def test_fixture_returns_tester_object(self, llm_eval) -> None:
        """Test that fixture returns a tester object with check method."""
        tester = llm_eval("Should return tester object")
        assert isinstance(tester, Tester)
        assert hasattr(tester, 'check')
        assert hasattr(tester, 'get_results')
        assert hasattr(tester, 'get_summary')

    @patch('numerous.pytest_llm_validate.fixture.get_agent')
    def test_tester_check_method_works(self, mock_get_agent: Mock, llm_eval) -> None:
        """Test that tester.check() method works correctly."""
        # Mock the agent evaluation
        from numerous.pytest_llm_validate.loader import get_default_rule
        
        mock_request = EvalRequest(
            specification="Test specification",
            artifacts={"output": "test output", "label": "test_label"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini"
        )
        
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.8,
            comment="Good output",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent
        
        tester = llm_eval("Test specification")
        # Should not raise an exception
        tester.check("test output", label="test_label")
        
        # Verify evaluation was called
        mock_agent.evaluate.assert_called_once()
        
        # Verify results are stored
        results = tester.get_results()
        assert len(results) == 1
        assert results[0].score == 0.8

    @patch('numerous.pytest_llm_validate.fixture.get_agent')
    def test_multiple_checks_supported(self, mock_get_agent: Mock, llm_eval) -> None:
        """Test that multiple check calls are supported."""
        # Mock the agent evaluation
        from numerous.pytest_llm_validate.loader import get_default_rule
        
        mock_request = EvalRequest(
            specification="All outputs should be professional",
            artifacts={"output": "test"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini"
        )
        
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.9,
            comment="Professional output",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent
        
        tester = llm_eval("All outputs should be professional")
        tester.check("First output", label="first")
        tester.check("Second output", label="second")
        
        # Verify both evaluations were called
        assert mock_agent.evaluate.call_count == 2
        
        # Verify results are stored
        results = tester.get_results()
        assert len(results) == 2
        
        # Test summary
        summary = tester.get_summary()
        assert summary["total_checks"] == 2
        assert summary["passed"] == 2
        assert summary["failed"] == 0

    def test_fixture_with_options(self, llm_eval) -> None:
        """Test that fixture accepts optional parameters."""
        tester = llm_eval(
            "Test with options",
            threshold=0.8,
            model="gpt-4o-mini"
        )
        assert isinstance(tester, Tester)
        assert tester.specification == "Test with options"
        assert tester.threshold == 0.8
        assert tester.model == "gpt-4o-mini"

    @patch('numerous.pytest_llm_validate.fixture.get_agent')
    def test_tester_check_failure(self, mock_get_agent: Mock, llm_eval) -> None:
        """Test that tester.check() raises AssertionError on failure."""
        # Mock the agent evaluation to fail
        from numerous.pytest_llm_validate.loader import get_default_rule
        
        mock_request = EvalRequest(
            specification="Should be high quality",
            artifacts={"output": "bad output"},
            rule=get_default_rule(),
            threshold=0.7,
            model="gpt-4o-mini"
        )
        
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.3,  # Below threshold
            comment="Poor quality",
            passed=False,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent
        
        tester = llm_eval("Should be high quality")
        
        with pytest.raises(AssertionError) as exc_info:
            tester.check("bad output", label="test_label")
        
        error_msg = str(exc_info.value)
        assert "LLM Evaluation Failed (test_label)" in error_msg
        assert "score: 0.30" in error_msg
        assert "Poor quality" in error_msg

    def test_tester_summary_empty(self, llm_eval) -> None:
        """Test tester summary when no checks have been performed."""
        tester = llm_eval("Test specification")
        summary = tester.get_summary()
        
        assert summary["total_checks"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["average_score"] == 0.0
        assert summary["checks"] == []

    @patch('numerous.pytest_llm_validate.fixture.get_agent')
    def test_tester_with_custom_rule(self, mock_get_agent: Mock, llm_eval) -> None:
        """Test tester with custom evaluation rule."""
        # Mock the agent evaluation
        from numerous.pytest_llm_validate.loader import get_rule
        
        test_rule = get_rule("test_behavior")  # Use the test_behavior rule
        assert test_rule is not None
        
        mock_request = EvalRequest(
            specification="Test with custom rule",
            artifacts={"output": "test output"},
            rule=test_rule,
            threshold=0.7,
            model="gpt-4o-mini"
        )
        
        mock_agent = Mock()
        mock_result = EvalResult(
            score=0.8,
            comment="Good test behavior",
            passed=True,
            request=mock_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00"
        )
        mock_agent.evaluate = AsyncMock(return_value=mock_result)
        mock_get_agent.return_value = mock_agent
        
        tester = llm_eval("Test with custom rule", rule="test_behavior")
        assert tester.eval_rule.name == "test_behavior"
        
        tester.check("test output")
        
        # Verify the correct rule was used
        call_args = mock_agent.evaluate.call_args[0][0]
        assert call_args.rule.name == "test_behavior"