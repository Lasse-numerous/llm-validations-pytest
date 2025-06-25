"""Comprehensive tests for numerous.pytest_llm_validate.models module."""

from datetime import datetime

import pytest

from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


class TestEvalRule:
    """Test cases for EvalRule model."""

    def test_create_basic_rule(self) -> None:
        """Test creating a basic EvalRule."""
        rule = EvalRule(
            name="test_rule",
            description="A test rule",
            prompt="Test prompt: {{specification}}",
        )

        assert rule.name == "test_rule"
        assert rule.description == "A test rule"
        assert rule.prompt == "Test prompt: {{specification}}"
        assert rule.version == "1.0"  # default
        assert rule.author == "pytest-llm-validate"  # default
        assert rule.tags == []  # default

    def test_create_full_rule(self) -> None:
        """Test creating a rule with all fields."""
        rule = EvalRule(
            name="advanced_rule",
            description="An advanced test rule",
            prompt="Advanced prompt: {{specification}} and {{artifacts}}",
            version="2.0",
            author="test_author",
            tags=["quality", "code_review"],
        )

        assert rule.name == "advanced_rule"
        assert rule.description == "An advanced test rule"
        assert rule.prompt == "Advanced prompt: {{specification}} and {{artifacts}}"
        assert rule.version == "2.0"
        assert rule.author == "test_author"
        assert rule.tags == ["quality", "code_review"]

    def test_rule_allows_empty_name(self) -> None:
        """Test that empty name is allowed (Pydantic default behavior)."""
        rule = EvalRule(name="", description="desc", prompt="prompt")
        assert rule.name == ""

    def test_rule_allows_empty_description(self) -> None:
        """Test that empty description is allowed (Pydantic default behavior)."""
        rule = EvalRule(name="name", description="", prompt="prompt")
        assert rule.description == ""

    def test_rule_allows_empty_prompt(self) -> None:
        """Test that empty prompt is allowed (Pydantic default behavior)."""
        rule = EvalRule(name="name", description="desc", prompt="")
        assert rule.prompt == ""


class TestEvalRequest:
    """Test cases for EvalRequest model."""

    @pytest.fixture
    def basic_rule(self) -> EvalRule:
        """Create a basic rule for testing."""
        return EvalRule(
            name="test_rule",
            description="Test rule",
            prompt="Evaluate: {{specification}}",
        )

    def test_create_basic_request(self, basic_rule: EvalRule) -> None:
        """Test creating a basic EvalRequest."""
        request = EvalRequest(
            specification="The code should be clean",
            artifacts={"code": "print('hello')"},
            rule=basic_rule,
        )

        assert request.specification == "The code should be clean"
        assert request.artifacts == {"code": "print('hello')"}
        assert request.rule == basic_rule
        assert request.threshold == 0.7  # default
        assert request.model == "gpt-4o-mini"  # default
        assert request.metadata == {}  # default

    def test_create_full_request(self, basic_rule: EvalRule) -> None:
        """Test creating a request with all fields."""
        metadata = {"test_id": "123", "user": "tester"}
        request = EvalRequest(
            specification="Code must be perfect",
            artifacts={"code": "def hello(): pass", "output": "result"},
            rule=basic_rule,
            threshold=0.9,
            model="gpt-4",
            metadata=metadata,
        )

        assert request.specification == "Code must be perfect"
        assert request.artifacts == {"code": "def hello(): pass", "output": "result"}
        assert request.rule == basic_rule
        assert request.threshold == 0.9
        assert request.model == "gpt-4"
        assert request.metadata == metadata

    def test_request_allows_empty_specification(self, basic_rule: EvalRule) -> None:
        """Test that empty specification is allowed (Pydantic default behavior)."""
        request = EvalRequest(
            specification="", artifacts={"code": "test"}, rule=basic_rule
        )
        assert request.specification == ""

    def test_request_validation_empty_artifacts(self, basic_rule: EvalRule) -> None:
        """Test validation with empty artifacts dict."""
        # Empty dict should be valid
        request = EvalRequest(specification="test spec", artifacts={}, rule=basic_rule)
        assert request.artifacts == {}

    def test_request_validation_invalid_threshold(self, basic_rule: EvalRule) -> None:
        """Test threshold validation."""
        # Negative threshold should be accepted by Pydantic (just a float)
        request = EvalRequest(
            specification="test",
            artifacts={"code": "test"},
            rule=basic_rule,
            threshold=-0.1,
        )
        assert request.threshold == -0.1


class TestEvalResult:
    """Test cases for EvalResult model."""

    @pytest.fixture
    def sample_request(self) -> EvalRequest:
        """Create a sample request for testing."""
        rule = EvalRule(name="test_rule", description="Test rule", prompt="Test prompt")
        return EvalRequest(
            specification="Test spec",
            artifacts={"code": "test"},
            rule=rule,
            threshold=0.8,
        )

    def test_create_basic_result(self, sample_request: EvalRequest) -> None:
        """Test creating a basic EvalResult."""
        result = EvalResult(
            score=0.85,
            comment="Good code quality",
            passed=True,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )

        assert result.score == 0.85
        assert result.comment == "Good code quality"
        assert result.passed is True
        assert result.request == sample_request
        assert result.model_used == "gpt-4o-mini"
        assert result.timestamp == "2024-01-01T00:00:00"

    def test_create_failing_result(self, sample_request: EvalRequest) -> None:
        """Test creating a failing result."""
        result = EvalResult(
            score=0.3,
            comment="Needs improvement",
            passed=False,
            request=sample_request,
            model_used="gpt-4",
            timestamp=datetime.now().isoformat(),
        )

        assert result.score == 0.3
        assert result.comment == "Needs improvement"
        assert result.passed is False
        assert result.request == sample_request
        assert result.model_used == "gpt-4"

    def test_passed_threshold_property_true(self, sample_request: EvalRequest) -> None:
        """Test passed_threshold property when score meets threshold."""
        result = EvalResult(
            score=0.9,  # Above threshold of 0.8
            comment="Excellent",
            passed=True,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )

        assert result.passed_threshold is True

    def test_passed_threshold_property_false(self, sample_request: EvalRequest) -> None:
        """Test passed_threshold property when score fails threshold."""
        result = EvalResult(
            score=0.5,  # Below threshold of 0.8
            comment="Needs work",
            passed=False,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )

        assert result.passed_threshold is False

    def test_passed_threshold_property_equal(self, sample_request: EvalRequest) -> None:
        """Test passed_threshold property when score equals threshold."""
        result = EvalResult(
            score=0.8,  # Equal to threshold of 0.8
            comment="Meets threshold",
            passed=True,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )

        assert result.passed_threshold is True

    def test_result_validation_invalid_score(self, sample_request: EvalRequest) -> None:
        """Test that invalid score types are handled."""
        # Pydantic should convert string to float if possible
        result = EvalResult(
            score="0.85",  # type: ignore
            comment="Test",
            passed=True,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        assert result.score == 0.85

    def test_result_allows_empty_comment(self, sample_request: EvalRequest) -> None:
        """Test that empty comment is allowed (Pydantic default behavior)."""
        result = EvalResult(
            score=0.85,
            comment="",
            passed=True,
            request=sample_request,
            model_used="gpt-4o-mini",
            timestamp="2024-01-01T00:00:00",
        )
        assert result.comment == ""
