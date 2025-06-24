"""Pytest configuration and fixtures for pytest-llm-validate tests."""

import pytest


@pytest.fixture
def llm_eval():
    """Placeholder llm_eval fixture that raises NotImplementedError.
    
    This is a placeholder fixture to make tests work during Phase 1.
    The actual implementation will be added in Phase 2.
    
    Raises:
        NotImplementedError: Always, until Phase 2 implementation
    """
    def _llm_eval(spec: str, **kwargs) -> None:  # type: ignore[misc]
        raise NotImplementedError("llm_eval fixture will be implemented in Phase 2")
    
    return _llm_eval