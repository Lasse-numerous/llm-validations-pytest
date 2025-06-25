"""Tests to ensure all model definitions are executed and measured for coverage."""

import inspect
from typing import get_type_hints

# Import the module to force execution of all lines
import numerous.pytest_llm_validate.models as models_module
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


def test_module_imports_execution() -> None:
    """Test that all module imports are executed and covered."""
    # Force import execution by accessing the module directly
    assert hasattr(models_module, "BaseModel")
    assert hasattr(models_module, "Field")
    assert hasattr(models_module, "Any")

    # Verify docstring is accessible
    assert models_module.__doc__ is not None
    assert "Core data models" in models_module.__doc__


def test_eval_rule_class_definition_execution() -> None:
    """Test that EvalRule class definition lines are executed."""
    # Access class attributes to force execution of class definition
    assert EvalRule.__name__ == "EvalRule"
    assert EvalRule.__doc__ is not None
    assert "rule containing prompts" in EvalRule.__doc__.lower()

    # Check that class inherits from BaseModel
    assert issubclass(EvalRule, models_module.BaseModel)

    # Access all field definitions to force their execution
    fields = EvalRule.model_fields
    assert "name" in fields
    assert "description" in fields
    assert "prompt" in fields
    assert "version" in fields
    assert "author" in fields
    assert "tags" in fields

    # Verify field descriptions (forces Field() execution)
    assert fields["name"].description == "Unique identifier for the rule"
    assert (
        fields["description"].description
        == "Human-readable description of what this rule evaluates"
    )
    assert fields["prompt"].description == "The actual LLM prompt template"
    assert fields["version"].description == "Version of the rule"
    assert fields["author"].description == "Author of the rule"
    assert fields["tags"].description == "Tags for categorizing rules"


def test_eval_request_class_definition_execution() -> None:
    """Test that EvalRequest class definition lines are executed."""
    # Access class attributes to force execution
    assert EvalRequest.__name__ == "EvalRequest"
    assert EvalRequest.__doc__ is not None
    assert "Request structure" in EvalRequest.__doc__

    # Check inheritance
    assert issubclass(EvalRequest, models_module.BaseModel)

    # Access all field definitions
    fields = EvalRequest.model_fields
    assert "specification" in fields
    assert "artifacts" in fields
    assert "rule" in fields
    assert "threshold" in fields
    assert "model" in fields
    assert "metadata" in fields

    # Verify field descriptions and defaults
    assert (
        fields["specification"].description
        == "Natural language specification from user"
    )
    assert fields["artifacts"].description == "Code outputs to evaluate"
    assert fields["rule"].description == "Rule to use for evaluation"
    assert fields["threshold"].description == "Minimum score threshold for passing"
    assert fields["model"].description == "LLM model to use"
    assert fields["metadata"].description == "Additional metadata"

    # Test default values
    assert fields["threshold"].default == 0.7
    assert fields["model"].default == "gpt-4o-mini"


def test_eval_result_class_definition_execution() -> None:
    """Test that EvalResult class definition lines are executed."""
    # Access class attributes
    assert EvalResult.__name__ == "EvalResult"
    assert EvalResult.__doc__ is not None
    assert "Result structure" in EvalResult.__doc__

    # Check inheritance
    assert issubclass(EvalResult, models_module.BaseModel)

    # Access all field definitions
    fields = EvalResult.model_fields
    assert "score" in fields
    assert "comment" in fields
    assert "passed" in fields
    assert "request" in fields
    assert "model_used" in fields
    assert "timestamp" in fields

    # Verify field descriptions
    assert fields["score"].description == "Numerical score between 0.0 and 1.0"
    assert fields["comment"].description == "Detailed explanation from the LLM"
    assert fields["passed"].description == "Whether the evaluation passed the threshold"
    assert (
        fields["request"].description == "Original request that generated this result"
    )
    assert fields["model_used"].description == "Actual model used for evaluation"
    assert fields["timestamp"].description == "ISO timestamp of evaluation"


def test_passed_threshold_property_execution() -> None:
    """Test that the passed_threshold property method is executed."""
    # Create instances to test the property
    rule = EvalRule(name="test", description="test", prompt="test")

    # Test passing threshold
    request_pass = EvalRequest(
        specification="test", artifacts={}, rule=rule, threshold=0.7
    )
    result_pass = EvalResult(
        score=0.8,
        comment="test",
        passed=True,
        request=request_pass,
        model_used="test",
        timestamp="2024-01-01T00:00:00",
    )

    # This should execute the property method
    assert result_pass.passed_threshold is True

    # Test failing threshold
    request_fail = EvalRequest(
        specification="test", artifacts={}, rule=rule, threshold=0.7
    )
    result_fail = EvalResult(
        score=0.5,
        comment="test",
        passed=False,
        request=request_fail,
        model_used="test",
        timestamp="2024-01-01T00:00:00",
    )

    # This should also execute the property method
    assert result_fail.passed_threshold is False

    # Test exact threshold
    result_exact = EvalResult(
        score=0.7,
        comment="test",
        passed=True,
        request=request_pass,  # threshold 0.7
        model_used="test",
        timestamp="2024-01-01T00:00:00",
    )

    assert result_exact.passed_threshold is True


def test_type_hints_execution() -> None:
    """Test that type hints are properly defined and accessible."""
    # Get type hints for all classes to force annotation execution
    eval_rule_hints = get_type_hints(EvalRule)
    eval_request_hints = get_type_hints(EvalRequest)
    eval_result_hints = get_type_hints(EvalResult)

    # Verify key type hints exist
    assert "name" in eval_rule_hints
    assert "description" in eval_rule_hints
    assert "tags" in eval_rule_hints

    assert "specification" in eval_request_hints
    assert "artifacts" in eval_request_hints
    assert "rule" in eval_request_hints

    assert "score" in eval_result_hints
    assert "comment" in eval_result_hints
    assert "request" in eval_result_hints


def test_method_signature_execution() -> None:
    """Test that method signatures are accessible and executed."""
    # Test property method signature
    prop_method = EvalResult.passed_threshold
    assert prop_method is not None

    # Check if it's a property
    assert isinstance(inspect.getattr_static(EvalResult, "passed_threshold"), property)

    # Test class method signatures
    assert hasattr(EvalRule, "model_fields")
    assert hasattr(EvalRequest, "model_fields")
    assert hasattr(EvalResult, "model_fields")


def test_field_factory_execution() -> None:
    """Test that field factory functions are executed."""
    # Test default_factory execution for tags and metadata
    rule = EvalRule(name="test", description="test", prompt="test")
    request = EvalRequest(specification="test", artifacts={}, rule=rule)

    # These should trigger the default_factory execution
    assert isinstance(rule.tags, list)
    assert rule.tags == []
    assert isinstance(request.metadata, dict)
    assert request.metadata == {}

    # Test with explicit values
    rule_with_tags = EvalRule(
        name="test", description="test", prompt="test", tags=["test", "example"]
    )
    assert rule_with_tags.tags == ["test", "example"]

    request_with_metadata = EvalRequest(
        specification="test", artifacts={}, rule=rule, metadata={"key": "value"}
    )
    assert request_with_metadata.metadata == {"key": "value"}


def test_all_model_classes_accessible() -> None:
    """Test that all model classes are accessible from the module."""
    # This forces the module-level class definitions to be executed
    assert hasattr(models_module, "EvalRule")
    assert hasattr(models_module, "EvalRequest")
    assert hasattr(models_module, "EvalResult")

    # Verify they are the same classes
    assert models_module.EvalRule is EvalRule
    assert models_module.EvalRequest is EvalRequest
    assert models_module.EvalResult is EvalResult
