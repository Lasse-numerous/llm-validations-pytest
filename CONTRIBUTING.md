# Contributing to pytest-LLM-Validate

We welcome contributions to pytest-LLM-Validate! This document outlines the development workflow, coding standards, and contribution process.

## Development Workflow

### Branching Strategy

We use a **feature-branch** workflow with **squash-on-merge**:

1. Create feature branches from `main`
2. Use descriptive branch names following the convention: `type/task#-short-desc`
3. Examples:
   - `feat/2.1-prompt-loader`
   - `fix/3.2-cli-serve`
   - `docs/7.1-mkdocs`
   - `test/6.2-integration-llm`

### Commit Message Convention

Follow conventional commits with the format: `type(scope): concise summary`

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `refactor`: Code refactoring

**Examples:**
- `feat(loader): add prompt loader`
- `test(decorator): verify simple case`
- `docs(contrib): outline workflow`
- `ci: add GitHub Actions workflows`

### Development Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/numerous-com/pytest-llm-validate
   cd pytest-llm-validate
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -e ".[dev]"
   ```

2. **Install pre-commit hooks (includes pytest):**
   ```bash
   pre-commit install
   ```

3. **Verify setup with pre-commit (runs all checks + tests):**
   ```bash
   pre-commit run --all-files
   ```

4. **Manual test execution:**
   ```bash
   # Run tests with coverage (CI configuration)
   pytest --cov=numerous.pytest_llm_validate --cov-report=term-missing --cov-fail-under=80

   # Quick test run (as used in pre-commit)
   pytest --tb=short -q --no-cov tests/
   ```

5. **Manual quality checks (automated in pre-commit):**
   ```bash
   ruff check .
   ruff format .
   mypy .
   bandit -r numerous/
   ```

## Code Standards

### Python Code Style

- **Python version**: 3.12+ (tested on 3.12 and 3.13)
- **Formatter**: `ruff format` (88 character line length)
- **Linter**: `ruff` with strict configuration
- **Type checker**: `mypy` in strict mode
- **Import sorting**: Handled by ruff

### Testing Requirements

- **Coverage**: 80% minimum required (enforced by CI)
- **Framework**: pytest with fixtures and parametrization
- **Mocking**: Use pytest-mock for external dependencies
- **Integration tests**: Mark with `@pytest.mark.integration`
- **LLM tests**: Mark with `@pytest.mark.llm` for tests requiring API calls
- **Pre-commit**: Tests run automatically on every commit via pre-commit hooks

### Pre-commit Quality Pipeline

Our pre-commit configuration provides comprehensive quality checking before every commit:

**Automated Checks (13 hooks):**
1. **Code Quality**: trailing whitespace, end-of-file, YAML/JSON/TOML validation
2. **Security**: debug statements check, bandit security scan
3. **Style**: ruff linting & formatting (ruff 0.12.0)
4. **Type Safety**: mypy type checking (mypy 1.16.1)
5. **Tests**: pytest execution with fast feedback (~0.05s)

**Configuration highlights:**
- All tool versions aligned with CI pipeline
- Pytest runs tests without coverage for speed
- Automatic cleanup of cache files
- MyPy checks test files for type safety

### Test-Driven Development (TDD)

We follow **TDD-first** approach:

1. Write failing tests first (red)
2. Implement minimal code to make tests pass (green)
3. Refactor while keeping tests green (refactor)

## Pull Request Process

### Before Opening a PR

1. **Run pre-commit (covers all quality checks + tests):**
   ```bash
   pre-commit run --all-files
   ```

2. **Verify CI compatibility with full coverage check:**
   ```bash
   pytest --cov=numerous.pytest_llm_validate --cov-report=term-missing --cov-fail-under=80
   ```

3. **Test package build (uses setuptools backend):**
   ```bash
   python -m build
   twine check dist/*
   ```

4. **Update documentation** if needed

### PR Guidelines

1. **Title**: Use conventional commit format
2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - Any breaking changes
   - Testing notes
3. **Link to issues** if applicable
4. **Request review** from maintainers

### PR Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- List of key changes made

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Integration tests pass (if applicable)
- [ ] 80% code coverage maintained (target: >80%)

## Breaking Changes
List any breaking changes or mark as N/A.

## Documentation
- [ ] README updated (if needed)
- [ ] Docstrings added/updated
- [ ] API documentation updated (if needed)
```

## Release Process

We use **semantic-release** for automated versioning and PyPI publishing:

1. Commits trigger version bumps based on conventional commit types
2. Releases are automatically created from `main` branch
3. PyPI publishing happens automatically on release

### Version Scheme

- `feat:` → minor version bump (0.1.0 → 0.2.0)
- `fix:` → patch version bump (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → major version bump (0.1.0 → 1.0.0)

## CI/CD Pipeline

Our GitHub Actions pipeline provides comprehensive validation:

**Build Matrix**: Python 3.12 and 3.13
**Pipeline Steps**:
1. **Lint**: ruff check + format validation + mypy type checking
2. **Test**: pytest with 80% coverage requirement
3. **Docs**: MkDocs build validation
4. **Security**: bandit security scanning
5. **Build**: Package building with setuptools + twine validation

**Key Features**:
- **Build System**: Uses setuptools (not hatchling) for reliable builds
- **Coverage**: Realistic 80% threshold (was 100%)
- **Documentation**: Automated MkDocs builds with material theme
- **Tool Alignment**: CI versions match pre-commit versions exactly

## Development Phases

The project follows a structured development plan with clear phases:

1. **Phase 1**: Repository & Toolchain Foundation (v0.1.0-rc1) ✅ **COMPLETED**
2. **Phase 2**: Core Library & Evaluation APIs (v0.1.0) ✅ **COMPLETED**
3. **Phase 3**: CLI Interface (v0.2.0)
4. **Phase 4**: FastAPI REST Backend (v0.3.0)
5. **Phase 5**: MCP Integration (v0.4.0)
6. **Phase 6**: Reporting & QA (v0.5.0)
7. **Phase 7**: Final Docs & Release (v1.0.0)

## Developer Workflow Best Practices

### Daily Development Cycle

1. **Start with pre-commit verification:**
   ```bash
   pre-commit run --all-files  # Ensures clean starting state
   ```

2. **Make changes following TDD:**
   - Write failing tests first
   - Implement minimal code to pass
   - Refactor while keeping tests green

3. **Commit frequently with meaningful messages:**
   ```bash
   git add .
   git commit -m "feat(loader): add rule validation"  # Pre-commit runs automatically
   ```

4. **Pre-PR verification:**
   ```bash
   # Full CI simulation
   pytest --cov=numerous.pytest_llm_validate --cov-report=term-missing --cov-fail-under=80
   python -m build && twine check dist/*
   ```

### Troubleshooting Common Issues

**Pre-commit fails with file modifications:**
- Some hooks modify files (ruff format, trailing whitespace)
- Run `git add .` and commit again

**MyPy type errors:**
- We use strict mode - no `Any` types allowed
- Add proper type annotations, especially for test functions

**Coverage below 80%:**
- Add tests for uncovered lines
- Use `pytest --cov --cov-report=html` for detailed coverage report

**Build failures:**
- We use setuptools (not hatchling)
- Check pyproject.toml for configuration issues

## Getting Help

- **Issues**: Open GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the [docs](https://pytest-llm-validate.readthedocs.io/)
- **CI/CD Issues**: See [CI_FIX_SUMMARY.md](CI_FIX_SUMMARY.md) for common CI problems
- **Pre-commit Setup**: See [PRECOMMIT_ALIGNMENT.md](PRECOMMIT_ALIGNMENT.md) for detailed configuration

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building this together!

## Environment Variables

For development and testing:

```bash
# Required for LLM integration tests
export OPENAI_API_KEY="your-api-key-here"

# Optional: Enable Logfire monitoring
export LOGFIRE_TOKEN="your-logfire-token"
```

## Maintainer Notes

See [docs/resume.md](docs/resume.md) for maintainer information and project context.
