"""pytest-llm-validate: AI-driven qualitative testing for pytest."""

__version__ = "0.1.0-rc2"

# Only expose the fixture-based functionality
# The decorator approach was removed as it violated pytest conventions
__all__: list[str] = []
