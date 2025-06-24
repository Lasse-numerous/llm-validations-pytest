# CI Debugging Guide

This guide provides comprehensive tools and techniques for debugging GitHub Actions CI runs for pytest-LLM-Validate.

## Overview

Our CI debugging toolkit includes:
- **Local CI simulation** (`scripts/debug-ci.sh`) - Reproduce CI environment locally
- **Real-time monitoring** (`scripts/monitor-ci.py`) - Monitor and analyze GitHub CI runs
- **Pre-commit integration** - Catch issues before they reach CI
- **Detailed logging** - Comprehensive error tracking and analysis

## Quick Start

### 1. Local CI Debugging (No GitHub Access Needed)

```bash
# Run all CI jobs locally
./scripts/debug-ci.sh all

# Run specific CI job
./scripts/debug-ci.sh test
./scripts/debug-ci.sh lint
./scripts/debug-ci.sh docs
```

### 2. GitHub CI Monitoring (Requires Authentication)

```bash
# Authenticate with GitHub (one-time setup)
gh auth login

# Check current CI status
python scripts/monitor-ci.py status

# Watch CI runs in real-time
python scripts/monitor-ci.py watch

# Analyze a failed CI run
python scripts/monitor-ci.py analyze <run-id>
```

## Local CI Simulation

### Available Commands

```bash
./scripts/debug-ci.sh <command>
```

**Commands:**
- `all` - Run all CI jobs (default)
- `lint` - Run linting job (ruff + mypy)
- `test` - Run test job with coverage
- `docs` - Run documentation build
- `security` - Run security scanning
- `build` - Run package build and validation
- `precommit` - Run pre-commit hooks simulation
- `analyze` - Analyze CI configuration
- `logs` - Show recent debug logs
- `cleanup` - Clean up CI artifacts

### Example Usage

```bash
# Check if there are any CI issues
./scripts/debug-ci.sh analyze

# Run the same checks as GitHub Actions
./scripts/debug-ci.sh all

# Debug a specific failure
./scripts/debug-ci.sh test
cat .ci-debug-logs/test-pytest-current.log

# Clean up after debugging
./scripts/debug-ci.sh cleanup
```

### Log Files

All debugging output is saved to `.ci-debug-logs/`:
```
.ci-debug-logs/
├── lint-ruff-check.log      # Ruff linting output
├── lint-mypy.log            # MyPy type checking output
├── test-pytest-current.log  # Test execution with coverage
├── docs-build.log           # MkDocs build output
├── security-bandit.log      # Security scan results
├── build-package.log        # Package build output
└── precommit.log           # Pre-commit hooks output
```

## GitHub CI Monitoring

### Setup

1. **Install GitHub CLI** (already done):
   ```bash
   gh --version  # Should show 2.74.2+
   ```

2. **Authenticate** (one-time):
   ```bash
   gh auth login
   # Follow prompts to authenticate
   ```

3. **Verify access**:
   ```bash
   python scripts/monitor-ci.py auth
   ```

### Monitoring Commands

```bash
python scripts/monitor-ci.py <command> [args]
```

**Commands:**
- `status` - Show current CI status and recent runs
- `watch [interval]` - Watch CI runs in real-time (default: 30s)
- `analyze <run-id>` - Analyze a specific CI run failure
- `logs <run-id> <job>` - Get logs for a specific job
- `auth` - Check GitHub CLI authentication status

### Example Workflows

**Check CI Status:**
```bash
python scripts/monitor-ci.py status
```
Output shows recent runs with color-coded status:
- ✓ Green: Success
- ✗ Red: Failure
- ⏳ Yellow: In Progress
- ? Blue: Other states

**Watch CI in Real-Time:**
```bash
# Watch with default 30-second interval
python scripts/monitor-ci.py watch

# Watch with custom interval
python scripts/monitor-ci.py watch 10
```

**Debug a Failed Run:**
```bash
# Get run ID from status command, then analyze
python scripts/monitor-ci.py analyze 1234567890

# Get specific job logs
python scripts/monitor-ci.py logs 1234567890 "test (3.12)"
```

## Common CI Issues and Solutions

### 1. Coverage Failures

**Symptoms:**
- `Coverage failure: total of 81 is less than fail-under=100`
- Tests pass but coverage is below threshold

**Local Debugging:**
```bash
# Run tests with detailed coverage report
pytest --cov=numerous.pytest_llm_validate --cov-report=html --cov-report=term-missing

# Open detailed coverage report
open htmlcov/index.html
```

**Solutions:**
- Add tests for uncovered lines
- Check if new code needs tests
- Review coverage exclusions in `pyproject.toml`

### 2. Type Checking Errors

**Symptoms:**
- `mypy` errors in CI logs
- Function missing type annotations
- Incompatible type assignments

**Local Debugging:**
```bash
# Run MyPy with detailed output
mypy . --show-error-codes --pretty

# Check specific file
mypy path/to/file.py
```

**Solutions:**
- Add type annotations to function signatures
- Import proper types from `typing` or `collections.abc`
- Fix `Any` types with specific types

### 3. Linting Errors

**Symptoms:**
- `ruff check` failures
- Code style violations (E/W/F codes)
- Import sorting issues

**Local Debugging:**
```bash
# Check and auto-fix issues
ruff check . --fix
ruff format .

# Check specific issues
ruff check . --show-source
```

**Solutions:**
- Run `ruff format .` to fix formatting
- Run `ruff check . --fix` to auto-fix issues
- Check `.pre-commit-config.yaml` for configuration

### 4. Test Failures

**Symptoms:**
- `FAILED` tests in CI
- `AssertionError` in test output
- Import errors in tests

**Local Debugging:**
```bash
# Run specific test with verbose output
pytest tests/test_file.py::test_function -v

# Run with debugger on failure
pytest tests/test_file.py --pdb

# Run only failed tests from last run
pytest --lf
```

**Solutions:**
- Check test mocking and fixtures
- Verify test data and expectations
- Check for environment-specific issues

### 5. Build Failures

**Symptoms:**
- Package build errors
- `twine check` failures
- Missing files in distribution

**Local Debugging:**
```bash
# Build package with verbose output
python -m build --verbose

# Check built package
twine check dist/*

# Inspect package contents
tar -tzf dist/*.tar.gz
```

**Solutions:**
- Check `pyproject.toml` configuration
- Verify file inclusions and exclusions
- Check setuptools configuration

## Automated Issue Detection

The monitoring script automatically detects common patterns:

### Pattern Matching

The system looks for these patterns in CI logs:

**Coverage Issues:**
- "Coverage failure"
- "total of X is less than fail-under"
- "Required test coverage of X not reached"

**Type Errors:**
- "error: " (MyPy)
- "incompatible type"
- "type ignore" comments

**Linting Issues:**
- Ruff error codes (E/W/F followed by numbers)
- "ruff check" failures

**Test Failures:**
- "FAILED"
- "AssertionError"
- "test.*failed"

**Import/Dependency Issues:**
- "ImportError"
- "ModuleNotFoundError"
- "No module named"

**Build Issues:**
- "build failed"
- "wheel.*failed"
- "twine.*failed"

### Automatic Suggestions

When patterns are detected, the system provides specific fix suggestions:

```bash
python scripts/monitor-ci.py analyze <run-id>
```

Example output:
```
[WARNING] Detected potential issues: Coverage failure, Type errors

Suggested fixes for Coverage failure:
  • Run: pytest --cov=numerous.pytest_llm_validate --cov-report=html
  • Check htmlcov/index.html for uncovered lines
  • Add tests for uncovered code or adjust coverage threshold

Suggested fixes for Type errors:
  • Run: mypy . --show-error-codes
  • Add type annotations for function parameters and returns
  • Check for Any types and replace with specific types
```

## Best Practices

### 1. Pre-emptive Debugging

```bash
# Before pushing changes
./scripts/debug-ci.sh all

# Before opening PR
python scripts/monitor-ci.py status
```

### 2. Continuous Monitoring

```bash
# Start monitoring when working on CI-sensitive changes
python scripts/monitor-ci.py watch &

# Check periodically
python scripts/monitor-ci.py status
```

### 3. Root Cause Analysis

```bash
# Don't just look at the failure - analyze the pattern
python scripts/monitor-ci.py analyze <run-id>

# Check related files and dependencies
./scripts/debug-ci.sh analyze
```

### 4. Local Reproduction

```bash
# Always try to reproduce locally first
./scripts/debug-ci.sh <job-type>

# Use the same Python version as CI
python3.12 -m pytest  # or python3.13
```

## Integration with Development Workflow

### Daily Usage

1. **Start of day**: Check CI status
   ```bash
   python scripts/monitor-ci.py status
   ```

2. **Before commit**: Run pre-commit simulation
   ```bash
   ./scripts/debug-ci.sh precommit
   ```

3. **After push**: Monitor CI progress
   ```bash
   python scripts/monitor-ci.py watch
   ```

4. **On failure**: Analyze and debug
   ```bash
   python scripts/monitor-ci.py analyze <run-id>
   ./scripts/debug-ci.sh <relevant-job>
   ```

### Team Collaboration

- **Share run IDs** for collaborative debugging
- **Use log files** for detailed error analysis
- **Document recurring issues** and solutions
- **Update patterns** in monitoring script as needed

## Troubleshooting the Debugging Tools

### GitHub CLI Issues

```bash
# Check authentication
gh auth status

# Re-authenticate if needed
gh auth login

# Check repository access
gh repo view
```

### Script Permissions

```bash
# Make scripts executable
chmod +x scripts/debug-ci.sh scripts/monitor-ci.py

# Check execution
./scripts/debug-ci.sh analyze
```

### Python Dependencies

```bash
# Ensure development dependencies are installed
pip install -e ".[dev]"

# Check Python version
python --version  # Should be 3.12+
```

## Advanced Usage

### Custom Pattern Detection

Edit `scripts/monitor-ci.py` to add custom failure patterns:

```python
patterns = {
    'Custom Issue': [
        'your-custom-pattern',
        'another-pattern'
    ]
}
```

### Log Analysis Scripts

Create custom analysis scripts using the log files:

```bash
# Analyze patterns across multiple runs
grep -r "specific-error" .ci-debug-logs/

# Compare logs between runs
diff .ci-debug-logs/test-pytest-run1.log .ci-debug-logs/test-pytest-run2.log
```

### Automated Alerts

Set up monitoring with notifications:

```bash
# Run monitoring in background with alerts
python scripts/monitor-ci.py watch > ci-status.log 2>&1 &

# Check for failures periodically
grep -q "Recent failures detected" ci-status.log && echo "CI failure alert!"
```

## Summary

This CI debugging toolkit provides:

✅ **Local simulation** of entire CI pipeline
✅ **Real-time monitoring** of GitHub Actions
✅ **Automated failure analysis** with pattern detection
✅ **Detailed logging** for debugging
✅ **Actionable suggestions** for common issues
✅ **Integration** with development workflow

Use these tools to catch issues early, debug failures quickly, and maintain a healthy CI pipeline!
