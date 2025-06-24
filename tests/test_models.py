"""Tests for the core data models."""

import pytest
from datetime import datetime
from numerous.pytest_llm_validate.models import EvalRule, EvalRequest, EvalResult


class TestEvalRule:
    """Test cases for EvalRule model."""
    
    def test_eval_rule_creation(self) -> None:
        """Test creating an EvalRule with all fields."""
        rule = EvalRule(
            name="test_rule",
            description="Test rule description",
            prompt="Test prompt content",
            version="2.0",
            author="test_author",
            tags=["test", "example"]
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "Test rule description"
        assert rule.prompt == "Test prompt content"
        assert rule.version == "2.0"
        assert rule.author == "test_author"
        assert rule.tags == ["test", "example"]
    
    def test_eval_rule_defaults(self) -> None:
        """Test EvalRule with default values."""
        rule = EvalRule(
            name="minimal_rule",
            description="Minimal rule",
            prompt="Basic prompt"
        )
        
        assert rule.name == "minimal_rule"
        assert rule.description == "Minimal rule"
        assert rule.prompt == "Basic prompt"
        assert rule.version == "1.0"  # Default
        assert rule.author == "pytest-llm-validate"  # Default
        assert rule.tags == []  # Default


class TestEvalRequest:
    """Test cases for EvalRequest model."""
    
    def test_eval_request_creation(self) -> None:
        """Test creating an EvalRequest with all fields."""
        rule = EvalRule(
            name="test_rule",
            description="Test rule",
            prompt="Test prompt"
        )
        
        request = EvalRequest(
            specification="Test specification",
            artifacts={"output": "test output", "code": "print('hello')"},
            rule=rule,
            threshold=0.8,
            model="gpt-4o-mini",
            metadata={"test_name": "example_test"}
        )
        
        assert request.specification == "Test specification"
        assert request.artifacts == {"output": "test output", "code": "print('hello')"}
        assert request.rule == rule
        assert request.threshold == 0.8
        assert request.model == "gpt-4o-mini"
        assert request.metadata == {"test_name": "example_test"}
    
    def test_eval_request_defaults(self) -> None:
        """Test EvalRequest with default values."""
        rule = EvalRule(
            name="test_rule",
            description="Test rule",
            prompt="Test prompt"
        )
        
        request = EvalRequest(
            specification="Test spec",
            artifacts={"output": "test"},
            rule=rule
        )
        
        assert request.threshold == 0.7  # Default
        assert request.model == "gpt-4o-mini"  # Default
        assert request.metadata == {}  # Default


class TestEvalResult:
    """Test cases for EvalResult model."""
    
    def test_eval_result_creation(self) -> None:
        """Test creating an EvalResult with all fields."""
        rule = EvalRule(
            name="test_rule",
            description="Test rule",
            prompt="Test prompt"
        )
        
        request = EvalRequest(
            specification="Test specification",
            artifacts={"output": "test output"},
            rule=rule,
            threshold=0.7
        )
        
        result = EvalResult(
            score=0.85,
            comment="Good quality output",
            passed=True,
            request=request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert result.score == 0.85
        assert result.comment == "Good quality output"
        assert result.passed is True
        assert result.request == request
        assert result.model_used == "gpt-4o-mini"
        assert result.timestamp == "2024-01-15T10:30:00Z"
    
    def test_passed_threshold_property(self) -> None:
        """Test the passed_threshold property calculation."""
        rule = EvalRule(
            name="test_rule",
            description="Test rule",
            prompt="Test prompt"
        )
        
        # Test case where score meets threshold
        request_passing = EvalRequest(
            specification="Test spec",
            artifacts={"output": "test"},
            rule=rule,
            threshold=0.7
        )
        
        result_passing = EvalResult(
            score=0.8,  # Above threshold
            comment="Passed",
            passed=True,
            request=request_passing,
            model_used="gpt-4o-mini",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert result_passing.passed_threshold is True
        
        # Test case where score doesn't meet threshold
        request_failing = EvalRequest(
            specification="Test spec",
            artifacts={"output": "test"},
            rule=rule,
            threshold=0.8
        )
        
        result_failing = EvalResult(
            score=0.6,  # Below threshold
            comment="Failed",
            passed=False,
            request=request_failing,
            model_used="gpt-4o-mini",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert result_failing.passed_threshold is False
        
        # Test edge case where score exactly meets threshold
        result_exact = EvalResult(
            score=0.8,  # Exactly at threshold
            comment="Exact match",
            passed=True,
            request=request_failing,  # threshold=0.8
            model_used="gpt-4o-mini",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert result_exact.passed_threshold is True