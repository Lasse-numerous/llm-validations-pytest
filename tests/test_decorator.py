"""Tests for the @llm_eval decorator functionality."""

import pytest
from numerous.pytest_llm_validate import llm_eval


class TestLLMEvalDecorator:
    """Test cases for @llm_eval decorator functionality."""

    def test_decorator_import_exists(self) -> None:
        """Test that llm_eval decorator can be imported."""
        # This should work once we create the __init__.py exports
        assert llm_eval is not None

    def test_decorator_raises_not_implemented(self) -> None:
        """Test that using @llm_eval decorator raises NotImplementedError."""
        
        @llm_eval("This should return a greeting")
        def test_greeting() -> str:
            return "Hello, World!"
        
        # The decorator should raise NotImplementedError when actually used
        with pytest.raises(NotImplementedError):
            test_greeting()

    def test_decorator_captures_docstring(self) -> None:
        """Test that decorator captures natural language specification."""
        
        @llm_eval("The function should return a polite greeting")
        def test_greeting_with_spec() -> str:
            return "Hello, World!"
        
        # This will fail until we implement the decorator logic
        with pytest.raises(NotImplementedError):
            test_greeting_with_spec()

    def test_decorator_captures_return_value(self) -> None:
        """Test that decorator captures test function return value."""
        
        @llm_eval("Should capture this return value")
        def test_return_capture() -> dict[str, str]:
            return {"message": "test output"}
        
        # This will fail until we implement artifact capture
        with pytest.raises(NotImplementedError):
            test_return_capture()

    def test_decorator_captures_stdout(self) -> None:
        """Test that decorator captures stdout from test execution."""
        
        @llm_eval("Should capture printed output")
        def test_stdout_capture() -> None:
            print("This should be captured")
            return None
        
        # This will fail until we implement stdout capture
        with pytest.raises(NotImplementedError):
            test_stdout_capture()