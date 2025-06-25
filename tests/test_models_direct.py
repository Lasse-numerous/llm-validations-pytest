"""Direct tests for numerous.pytest_llm_validate.models module to ensure coverage."""

from datetime import datetime

from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


def test_models_module_imports() -> None:
    """Test that all models can be imported directly."""
    # This ensures the import lines are covered
    from numerous.pytest_llm_validate.models import (
        EvalRequest,
        EvalResult,
        EvalRule,
    )

    assert EvalRule is not None
    assert EvalRequest is not None
    assert EvalResult is not None


def test_eval_rule_direct_instantiation() -> None:
    """Test direct instantiation of EvalRule to ensure class definition coverage."""
    rule = EvalRule(name="test_rule", description="A test rule", prompt="Test prompt")

    # Test all fields are accessible (covers field definitions)
    assert rule.name == "test_rule"
    assert rule.description == "A test rule"
    assert rule.prompt == "Test prompt"
    assert rule.version == "1.0"
    assert rule.author == "pytest-llm-validate"
    assert rule.tags == []


def test_eval_request_direct_instantiation() -> None:
    """Test direct instantiation of EvalRequest to ensure class definition coverage."""
    rule = EvalRule(name="test", description="test", prompt="test")
    request = EvalRequest(
        specification="Test spec", artifacts={"code": "test"}, rule=rule
    )

    # Test all fields are accessible (covers field definitions)
    assert request.specification == "Test spec"
    assert request.artifacts == {"code": "test"}
    assert request.rule == rule
    assert request.threshold == 0.7
    assert request.model == "gpt-4o-mini"
    assert request.metadata == {}


def test_eval_result_direct_instantiation() -> None:
    """Test direct instantiation of EvalResult to ensure class definition coverage."""
    rule = EvalRule(name="test", description="test", prompt="test")
    request = EvalRequest(
        specification="Test spec", artifacts={"code": "test"}, rule=rule
    )

    result = EvalResult(
        score=0.85,
        comment="Good quality",
        passed=True,
        request=request,
        model_used="gpt-4o-mini",
        timestamp=datetime.now().isoformat(),
    )

    # Test all fields are accessible (covers field definitions)
    assert result.score == 0.85
    assert result.comment == "Good quality"
    assert result.passed is True
    assert result.request == request
    assert result.model_used == "gpt-4o-mini"
    assert result.timestamp is not None


def test_eval_result_passed_threshold_property() -> None:
    """Test the passed_threshold property to ensure method coverage."""
    rule = EvalRule(name="test", description="test", prompt="test")
    request = EvalRequest(
        specification="Test spec", artifacts={"code": "test"}, rule=rule, threshold=0.8
    )

    # Test property with passing score
    result_pass = EvalResult(
        score=0.9,
        comment="Excellent",
        passed=True,
        request=request,
        model_used="gpt-4o-mini",
        timestamp="2024-01-01T00:00:00",
    )
    assert result_pass.passed_threshold is True

    # Test property with failing score
    result_fail = EvalResult(
        score=0.5,
        comment="Needs work",
        passed=False,
        request=request,
        model_used="gpt-4o-mini",
        timestamp="2024-01-01T00:00:00",
    )
    assert result_fail.passed_threshold is False

    # Test property with exact threshold
    result_exact = EvalResult(
        score=0.8,
        comment="Meets threshold",
        passed=True,
        request=request,
        model_used="gpt-4o-mini",
        timestamp="2024-01-01T00:00:00",
    )
    assert result_exact.passed_threshold is True


def test_field_types_and_defaults() -> None:
    """Test field types and default values to ensure Field definitions are covered."""
    # Test EvalRule defaults
    rule = EvalRule(name="test", description="test", prompt="test")
    assert isinstance(rule.version, str)
    assert isinstance(rule.author, str)
    assert isinstance(rule.tags, list)

    # Test EvalRequest defaults
    request = EvalRequest(specification="test", artifacts={}, rule=rule)
    assert isinstance(request.threshold, float)
    assert isinstance(request.model, str)
    assert isinstance(request.metadata, dict)

    # Test with explicit metadata
    request_with_meta = EvalRequest(
        specification="test", artifacts={}, rule=rule, metadata={"key": "value"}
    )
    assert request_with_meta.metadata == {"key": "value"}


def test_pydantic_field_descriptions() -> None:
    """Test that pydantic Field descriptions are accessible."""
    rule = EvalRule(name="test", description="test", prompt="test")

    # Access the model fields to ensure Field definitions are covered
    fields = rule.model_fields
    assert "name" in fields
    assert "description" in fields
    assert "prompt" in fields
    assert "version" in fields
    assert "author" in fields
    assert "tags" in fields

    # Test field descriptions exist
    assert fields["name"].description is not None
    assert fields["description"].description is not None
    assert fields["prompt"].description is not None
