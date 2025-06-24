"""pytest-LLM-Validate: A pytest plugin for AI-driven qualitative & behavioural tests."""

__version__ = "0.1.0-rc1"

# Import the real implementation
from .decorator import llm_eval

__all__ = ["__version__", "llm_eval"]
