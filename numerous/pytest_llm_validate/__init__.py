"""pytest-LLM-Validate: A pytest plugin for AI-driven qualitative & behavioural tests."""

__version__ = "0.1.0-rc1"


def llm_eval(spec: str, **kwargs) -> None:  # type: ignore[misc]
    """Placeholder llm_eval decorator/fixture that raises NotImplementedError.
    
    This is a placeholder implementation to make imports work during Phase 1.
    The actual implementation will be added in Phase 2.
    
    Args:
        spec: Natural language specification for evaluation
        **kwargs: Optional parameters (threshold, model, etc.)
        
    Raises:
        NotImplementedError: Always, until Phase 2 implementation
    """
    raise NotImplementedError("llm_eval will be implemented in Phase 2")


__all__ = ["__version__", "llm_eval"]