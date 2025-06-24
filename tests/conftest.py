"""Pytest configuration and fixtures for pytest-llm-validate tests."""

import pytest

# Import and register the plugin manually for testing
pytest_plugins = ["numerous.pytest_llm_validate.plugin"]