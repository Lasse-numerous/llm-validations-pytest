# Developer Workflow Guide

This guide provides detailed information about the development workflow, toolchain, and best practices for contributing to pytest-LLM-Validate.

## Overview

pytest-LLM-Validate follows a **quality-first development approach** with comprehensive automation to ensure code quality, type safety, and test coverage. Our workflow is designed to catch issues early and provide fast feedback to developers.

## Development Environment Setup

### Prerequisites

- **Python**: 3.12+ (we test on 3.12 and 3.13)
- **Git**: For version control
- **OpenAI API Key**: For LLM integration tests (optional for most development)

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/numerous-com/pytest-llm-validate
cd pytest-llm-validate

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Install pre-commit hooks (including commit message validation)
pre-commit install
pre-commit install --hook-type commit-msg

# 5. Verify setup
pre-commit run --all-files
```

## Development Workflow

### 1. Feature Development Cycle

**Start a new feature:**
```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feat/your-feature-name

# 2. Verify clean starting state
pre-commit run --all-files
```

**Follow TDD approach:**
```bash
# 1. Write failing tests first (RED)
# 2. Run tests to confirm they fail
pytest tests/test_your_feature.py -v

# 3. Implement minimal code to pass (GREEN)
# 4. Run tests to confirm they pass
pytest tests/test_your_feature.py -v

# 5. Refactor while keeping tests green (REFACTOR)
# 6. Verify all tests still pass
pytest
```

**Commit frequently with conventional format:**
```bash
git add .
git commit -m "feat(core): add feature description"
# Pre-commit hooks run automatically and must pass
# Conventional commit format is validated and enforced
```

### 2. Quality Assurance

Our pre-commit pipeline runs **11 regular hooks** + **1 commit-msg hook** automatically:

**Regular Hooks (every commit):**
- **Code Quality**: Trailing whitespace, end-of-file, YAML/JSON/TOML validation
- **Security**: Debug statement detection, bandit security scanning
- **Testing**: Pytest execution (~0.05s) with automatic cleanup
- **Documentation**: MkDocs build validation

**Commit Message Hook:**
- **Conventional Commits**: Format validation with required scopes

**Pre-push Hooks:**
- **CI Simulation**: Comprehensive linting, type checking, testing, and commit validation

**Configuration highlights:**
- No duplicate tool execution (CI simulation handles ruff/mypy for pre-push)
- Pytest runs without coverage for speed in regular commits
- Conventional commit validation prevents invalid commit messages

### 3. Manual Quality Checks

When needed, you can run individual tools:

```bash
# Formatting and linting
ruff check .                    # Check for issues
ruff format .                   # Auto-format code
ruff check . --fix              # Fix auto-fixable issues

# Type checking
mypy .                          # Check all files
mypy numerous/                  # Check specific directory

# Security scanning
bandit -r numerous/             # Scan for security issues

# Testing with coverage (CI configuration)
pytest --cov=numerous.pytest_llm_validate --cov-report=term-missing --cov-fail-under=80

# Build testing
python -m build                 # Build distribution packages
twine check dist/*              # Validate packages
```

### 4. Pre-Pull Request Checklist

**Before opening a PR:**

```bash
# 1. Run full pre-commit suite
pre-commit run --all-files

# 2. Verify CI compatibility
pytest --cov=numerous.pytest_llm_validate --cov-report=term-missing --cov-fail-under=80

# 3. Test package build
python -m build
twine check dist/*

# 4. Ensure documentation is updated
mkdocs build --strict

# 5. Verify branch is up-to-date
git fetch origin
git rebase origin/main  # if needed
```

## Commit Message Standards

### Conventional Commits (Required)

**All commits must follow conventional commit format with mandatory scopes.**

**Format: `type(scope): description`**

**Valid Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `test` - Testing changes
- `build` - Build system changes
- `ci` - CI/CD changes
- `chore` - Maintenance tasks
- `revert` - Revert previous changes

**Valid Scopes (Required):**
- `core` - Core functionality
- `test` - Testing infrastructure
- `docs` - Documentation
- `ci` - CI/CD pipeline
- `build` - Build system
- `config` - Configuration
- `scripts` - Utility scripts
- `api` - API changes
- `cli` - Command line interface
- `web` - Web interface
- `data` - Data handling
- `security` - Security features
- `deps` - Dependencies

**Examples:**
```bash
feat(core): add new authentication system
fix(test): resolve failing unit tests
docs(api): update endpoint documentation
chore(deps): update project dependencies
ci(build): optimize GitHub Actions workflow
refactor(scripts): improve debugging tools
```

**Validation:**
- ✅ **Commit-msg hook**: Validates format on every commit
- ✅ **Pre-push CI**: Double-checks format before remote push
- ❌ **Enforcement**: Invalid commits are automatically rejected

## Code Standards

### Python Code Quality

**Style Requirements:**
- **Line Length**: 88 characters (ruff format)
- **Import Sorting**: Automatic via ruff
- **Type Hints**: Required for all functions (mypy strict mode)
- **Docstrings**: Required for public APIs

**Code Organization:**
```python
# Import order (handled by ruff)
from __future__ import annotations  # if needed

# Standard library imports
import asyncio
import json
from typing import Any

# Third-party imports
import pytest
from pydantic import BaseModel

# Local imports
from numerous.pytest_llm_validate.models import EvalRule
```

### Testing Standards

**Coverage Requirements:**
- **Minimum**: 80% (enforced by CI)
- **Target**: >85% for good quality
- **Exclude**: Only test files and `__main__` blocks

**Test Organization:**
```python
# tests/test_feature.py
"""Tests for feature functionality."""

from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest

from numerous.pytest_llm_validate.feature import Feature


class TestFeature:
    """Test cases for Feature class."""

    def test_basic_functionality(self) -> None:
        """Test basic feature behavior."""
        # Arrange
        feature = Feature()

        # Act
        result = feature.do_something()

        # Assert
        assert result is not None
```

**Test Categories:**
- **Unit tests**: Fast, isolated, mocked dependencies
- **Integration tests**: Mark with `@pytest.mark.integration`
- **LLM tests**: Mark with `@pytest.mark.llm` (require API key)

### Type Safety

**MyPy Configuration:**
- **Strict mode**: Enabled
- **No Any types**: Discouraged
- **Type annotations**: Required for all function signatures

**Common Type Patterns:**
```python
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

# Function signatures
def process_data(items: Sequence[str]) -> list[str]:
    """Process a sequence of strings."""
    return [item.strip() for item in items]

# Generic types
T = TypeVar('T')

def get_first(items: Sequence[T]) -> T | None:
    """Get first item or None."""
    return items[0] if items else None

# Pytest fixtures
def my_fixture() -> Callable[..., str]:
    """Return a callable that takes any args and returns str."""
    def inner(*args: Any, **kwargs: Any) -> str:
        return "result"
    return inner
```

## CI/CD Pipeline

### GitHub Actions Workflow

Our CI pipeline runs on **Python 3.12 and 3.13** with these jobs:

**1. Lint Job:**
- Ruff check and format validation
- MyPy type checking

**2. Test Job:**
- Pytest with 80% coverage requirement
- Runs on both Python versions
- Codecov upload for coverage tracking

**3. Docs Job:**
- MkDocs build validation
- Ensures documentation builds successfully

**4. Security Job:**
- Bandit security scanning
- Artifact upload for security reports

**5. Build Job:**
- Package building with setuptools
- Twine validation of distribution packages

### Build System

**Configuration (pyproject.toml):**
```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"
```

**Key Changes:**
- Uses **setuptools** (not hatchling) for reliable builds
- **Coverage threshold**: 80% (reduced from 100%)
- **Tool versions**: Aligned between CI and pre-commit

## Project Architecture

### Code Organization

```
numerous/
├── __init__.py                 # Package root
└── pytest_llm_validate/
    ├── __init__.py            # Main plugin exports
    ├── agent.py               # PydanticAI integration
    ├── decorator.py           # @llm_eval decorator
    ├── fixture.py             # llm_eval fixture
    ├── history.py             # Deduplication cache
    ├── loader.py              # Rule loading system
    ├── models.py              # Pydantic data models
    ├── plugin.py              # Pytest plugin entry
    └── rules/                 # Built-in evaluation rules
        ├── __init__.py
        ├── general_quality.mdc
        ├── output_format.mdc
        └── test_behavior.mdc
```

### Key Design Principles

**1. Dual API Design:**
- **Decorator API**: `@llm_eval("spec")` for simple cases
- **Fixture API**: `llm_eval("spec").check(output)` for complex scenarios

**2. Quality Assurance:**
- Pre-commit hooks for immediate feedback
- CI pipeline for comprehensive validation
- Type safety with mypy strict mode

**3. Developer Experience:**
- Minimal setup with automatic tool installation
- Fast feedback loops with optimized pre-commit
- Clear error messages and troubleshooting guides

**4. Extensibility:**
- Plugin architecture for pytest integration
- Rule system for customizable evaluation criteria
- Multi-interface support (core → CLI → REST → MCP)

## Troubleshooting

### Common Development Issues

**Problem: Pre-commit modifying files**
```bash
# Some hooks auto-fix issues (formatting, whitespace)
# Solution: Add changes and commit again
git add .
git commit -m "fix: address pre-commit formatting"
```

**Problem: MyPy type errors**
```bash
# Strict mode requires explicit types
# Solution: Add proper type annotations
def my_function(data: dict[str, Any]) -> str:
    return str(data)
```

**Problem: Coverage below 80%**
```bash
# Solution: Add tests or check coverage report
pytest --cov --cov-report=html
open htmlcov/index.html  # View detailed coverage
```

**Problem: Build failures**
```bash
# Check setuptools configuration
python -m build --verbose
# Common issues: missing files, incorrect package structure
```

### Performance Optimization

**Pre-commit Speed:**
- Tests run in ~0.05s without coverage
- Use `pytest --no-cov` for fastest execution
- Cache is automatically cleaned after each run

**Development Workflow:**
- Use `pre-commit run <hook-name>` for individual hooks
- Use `pytest -k "test_name"` for specific tests
- Use `pytest --lf` to run only last failed tests

## References

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Ruff Configuration](https://docs.astral.sh/ruff/)
- [MyPy Strict Mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## Next Steps

After mastering the basic workflow:

1. **Phase 3**: CLI Interface development
2. **Phase 4**: FastAPI REST backend
3. **Phase 5**: MCP integration
4. **Advanced**: Custom rule development
5. **Enterprise**: Monitoring and reporting features

For questions or suggestions about the workflow, please open a GitHub Discussion or refer to the project maintainers in [docs/resume.md](resume.md).
