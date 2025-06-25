"""Tests for numerous.pytest_llm_validate.__init__ module."""

import numerous.pytest_llm_validate


def test_version_is_defined() -> None:
    """Test that the version is properly defined."""
    assert hasattr(numerous.pytest_llm_validate, "__version__")
    assert numerous.pytest_llm_validate.__version__ == "0.1.0-rc2"


def test_all_is_defined() -> None:
    """Test that __all__ is properly defined."""
    assert hasattr(numerous.pytest_llm_validate, "__all__")
    assert isinstance(numerous.pytest_llm_validate.__all__, list)
