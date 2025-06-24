"""Tests for the rule loader functionality."""

import pytest
from numerous.pytest_llm_validate.loader import RuleLoader, load_rules, get_rule, get_default_rule
from numerous.pytest_llm_validate.models import EvalRule


class TestRuleLoader:
    """Test cases for rule loading functionality."""

    def test_loader_creation_succeeds(self) -> None:
        """Test that RuleLoader creation works correctly."""
        loader = RuleLoader()
        assert loader is not None
        assert len(loader.get_all_rules()) >= 3  # We have 3 packaged rules

    def test_load_rules_returns_dict(self) -> None:
        """Test that load_rules method returns a dictionary of rules."""
        rules = load_rules()
        assert isinstance(rules, dict)
        assert len(rules) >= 3  # Expect at least our 3 packaged rules
        
        # Check that all expected rules are present
        expected_rules = {"general_quality", "test_behavior", "output_format"}
        assert expected_rules.issubset(set(rules.keys()))

    def test_rule_count_validation(self) -> None:
        """Test that loaded rules have expected count."""
        rules = load_rules()
        assert len(rules) >= 3  # Expect at least our 3 packaged rules
        
        # Verify specific rules exist
        assert "general_quality" in rules
        assert "test_behavior" in rules
        assert "output_format" in rules

    def test_rule_fields_validation(self) -> None:
        """Test that loaded rules have expected fields."""
        rules = load_rules()
        for rule_name, rule in rules.items():
            assert isinstance(rule, EvalRule)
            assert hasattr(rule, 'name')
            assert hasattr(rule, 'prompt')
            assert hasattr(rule, 'description')
            assert hasattr(rule, 'version')
            assert hasattr(rule, 'author')
            assert hasattr(rule, 'tags')
            
            # Verify types
            assert isinstance(rule.name, str)
            assert isinstance(rule.prompt, str)
            assert isinstance(rule.description, str)
            assert isinstance(rule.version, str)
            assert isinstance(rule.author, str)
            assert isinstance(rule.tags, list)
    
    def test_get_specific_rule(self) -> None:
        """Test getting a specific rule by name."""
        rule = get_rule("general_quality")
        assert rule is not None
        assert rule.name == "general_quality"
        assert "quality" in rule.description.lower()
        
        # Test non-existent rule
        missing_rule = get_rule("non_existent_rule")
        assert missing_rule is None
    
    def test_get_default_rule(self) -> None:
        """Test getting the default rule."""
        default_rule = get_default_rule()
        assert default_rule is not None
        assert isinstance(default_rule, EvalRule)
        # Should prefer general_quality as default
        assert default_rule.name == "general_quality"
    
    def test_rule_content_parsing(self) -> None:
        """Test that rule content is parsed correctly from .mdc files."""
        rule = get_rule("general_quality")
        assert rule is not None
        
        # Check that metadata was parsed correctly
        assert rule.version == "1.0"
        assert rule.author == "pytest-llm-validate"
        assert "quality" in rule.tags
        assert "general" in rule.tags
        assert "correctness" in rule.tags
        
        # Check that prompt was extracted
        assert len(rule.prompt) > 100  # Should be substantial content
        assert "specification" in rule.prompt.lower()
        assert "artifacts" in rule.prompt.lower()
    
    def test_loader_singleton_pattern(self) -> None:
        """Test that the loader follows singleton pattern."""
        from numerous.pytest_llm_validate.loader import get_loader
        
        loader1 = get_loader()
        loader2 = get_loader()
        assert loader1 is loader2  # Same instance
    
    def test_fallback_rule_when_no_rules_loaded(self) -> None:
        """Test that fallback rule is used when no rules are loaded."""
        # Create a new loader instance and clear its cache to simulate no rules
        loader = RuleLoader()
        loader._rules_cache.clear()  # Force empty cache
        
        fallback_rule = loader.get_default_rule()
        assert fallback_rule is not None
        assert fallback_rule.name == "fallback"
        assert "fallback" in fallback_rule.description.lower()
        assert fallback_rule.tags == ["fallback"]
    
    def test_empty_rules_cache_scenarios(self) -> None:
        """Test various scenarios with empty rules cache."""
        loader = RuleLoader()
        loader._rules_cache.clear()  # Force empty cache
        
        # Test get_rule returns None for empty cache
        assert loader.get_rule("any_rule") is None
        
        # Test list_rule_names returns empty list
        assert loader.list_rule_names() == []
        
        # Test get_all_rules returns empty dict
        assert loader.get_all_rules() == {}
    
    def test_fallback_directory_loading(self) -> None:
        """Test that fallback directory loading works in development."""
        from pathlib import Path
        
        # Create a new loader to test fallback loading
        # This tests the except block in _load_packaged_rules
        loader = RuleLoader()
        
        # Should still have loaded rules from the fallback path
        assert len(loader.get_all_rules()) >= 3  # Should find our rules
    
    def test_metadata_extraction_edge_cases(self) -> None:
        """Test metadata extraction with various edge cases."""
        loader = RuleLoader()
        
        # Test with minimal content
        minimal_content = """
**Name:** test_rule
**Description:** Test description

## Evaluation Prompt
Basic prompt content
"""
        rule = loader._parse_mdc_content(minimal_content, "test")
        assert rule.name == "test_rule"
        assert rule.description == "Test description"
        assert rule.version == "1.0"  # Default value
        assert rule.author == "pytest-llm-validate"  # Default value
        assert rule.tags == []  # Default value
        
        # Test with tags
        content_with_tags = """
**Name:** tagged_rule
**Description:** Rule with tags
**Tags:** tag1, tag2, tag3

## Evaluation Prompt
Prompt content
"""
        rule = loader._parse_mdc_content(content_with_tags, "tagged")
        assert rule.tags == ["tag1", "tag2", "tag3"]
    
    def test_prompt_extraction_edge_cases(self) -> None:
        """Test prompt extraction with various content structures."""
        loader = RuleLoader()
        
        # Test with no evaluation prompt section
        no_prompt_section = """
**Name:** no_prompt
**Description:** No prompt section

Some content here
"""
        rule = loader._parse_mdc_content(no_prompt_section, "test")
        assert len(rule.prompt) > 0  # Should extract something
        
        # Test with multiple ## sections
        multiple_sections = """
**Name:** multi_section
**Description:** Multiple sections

## Evaluation Prompt
This is the prompt content

## Other Section
This should not be included in prompt
"""
        rule = loader._parse_mdc_content(multiple_sections, "test")
        assert "This is the prompt content" in rule.prompt
        assert "Other Section" not in rule.prompt
        
        # Test fallback prompt extraction (line 96 coverage)
        content_with_generic_section = """
**Name:** generic_section
**Description:** Content with generic section

## Some Section
This content should be extracted as prompt
"""
        rule = loader._parse_mdc_content(content_with_generic_section, "test")
        assert "This content should be extracted as prompt" in rule.prompt
    
    def test_exception_handling_coverage(self) -> None:
        """Test exception handling in _load_packaged_rules to cover lines 33-42."""
        import unittest.mock
        
        # Mock importlib.resources.files to raise an exception
        with unittest.mock.patch('importlib.resources.files', side_effect=ImportError("Mocked error")):
            # This should trigger the exception handling block
            loader = RuleLoader()
            
            # Should still load rules from fallback directory method
            assert len(loader.get_all_rules()) >= 3
    
    def test_global_loader_instance_creation(self) -> None:
        """Test the global loader instance creation to cover line 118."""
        # Import a fresh copy of the module to test singleton creation
        import importlib
        import sys
        
        # Remove the module from cache to force fresh import
        module_name = 'numerous.pytest_llm_validate.loader'
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Import fresh module - this should trigger line 118 when get_loader() is first called
        import numerous.pytest_llm_validate.loader as loader_module
        
        # The module should start with _loader_instance = None
        # First call to get_loader() should create the instance (line 118)
        loader = loader_module.get_loader()
        assert loader is not None
        
        # Verify it's a singleton
        loader2 = loader_module.get_loader()
        assert loader is loader2