"""Tests for the rule loader functionality."""

import pytest
from numerous.pytest_llm_validate.loader import RuleLoader


class TestRuleLoader:
    """Test cases for rule loading functionality."""

    def test_loader_creation_raises_not_implemented(self) -> None:
        """Test that RuleLoader creation raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            RuleLoader()

    def test_load_rules_raises_not_implemented(self) -> None:
        """Test that load_rules method raises NotImplementedError."""
        # This test will fail initially since the loader doesn't exist
        with pytest.raises((NotImplementedError, ImportError)):
            from numerous.pytest_llm_validate.loader import load_rules
            load_rules()

    def test_rule_count_validation(self) -> None:
        """Test that loaded rules have expected count (placeholder test)."""
        # This test will fail until we implement the loader
        with pytest.raises((NotImplementedError, ImportError)):
            from numerous.pytest_llm_validate.loader import load_rules
            rules = load_rules()
            assert len(rules) > 0  # Expect at least one packaged rule

    def test_rule_fields_validation(self) -> None:
        """Test that loaded rules have expected fields (placeholder test)."""
        # This test will fail until we implement the loader and EvalRule model
        with pytest.raises((NotImplementedError, ImportError)):
            from numerous.pytest_llm_validate.loader import load_rules
            rules = load_rules()
            for rule in rules:
                assert hasattr(rule, 'name')
                assert hasattr(rule, 'prompt')
                assert hasattr(rule, 'description')