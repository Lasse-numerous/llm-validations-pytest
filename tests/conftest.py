"""Pytest configuration and fixtures for pytest-llm-validate tests."""

# The plugin is automatically registered via entry point in pyproject.toml
# No manual registration needed here

# Import all modules to ensure coverage measurement
import numerous.pytest_llm_validate
import numerous.pytest_llm_validate.agent
import numerous.pytest_llm_validate.decorator
import numerous.pytest_llm_validate.fixture
import numerous.pytest_llm_validate.history
import numerous.pytest_llm_validate.loader
import numerous.pytest_llm_validate.models
import numerous.pytest_llm_validate.plugin
