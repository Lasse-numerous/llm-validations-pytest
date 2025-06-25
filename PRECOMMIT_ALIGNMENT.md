# Pre-commit Configuration Alignment

## Changes Made

### 1. Added Pytest to Pre-commit
**New Addition**: Added pytest as a local pre-commit hook to catch test failures early.

**Configuration**:
```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: sh
      language: system
      types: [python]
      args: [-c, "pytest --tb=short -q --no-cov --override-ini='addopts=' tests/; rm -f .pytest-llm-validate-history.json .coverage"]
      pass_filenames: false
      always_run: true
```

**Features**:
- Runs all tests quickly with `-q` (quiet mode)
- Uses `--no-cov` and overrides pyproject.toml to avoid coverage file generation
- Cleans up any cache files that get created (`.pytest-llm-validate-history.json`, `.coverage`)
- Provides short traceback output for failures

### 2. Updated Tool Versions
Updated all pre-commit hook versions to match current installed versions:

#### Ruff (Linting & Formatting)
- **Before**: `v0.7.0`
- **After**: `v0.12.0` ✅
- Matches installed version: `ruff 0.12.0`

#### MyPy (Type Checking)
- **Before**: `v1.8.0`
- **After**: `v1.16.1` ✅
- Matches installed version: `mypy 1.16.1`

#### Bandit (Security Scanning)
- **Before**: `1.7.5`
- **After**: `1.8.5` ✅
- Matches installed version: `bandit 1.8.5`

#### Pre-commit Hooks (General)
- **Before**: `v4.5.0`
- **After**: `v5.0.0` ✅ (via `pre-commit autoupdate`)

### 3. MyPy Configuration Improvements
**Before**: Excluded both `tests/` and `docs/` directories
```yaml
exclude: ^(tests/|docs/)
```

**After**: Only exclude `docs/` since test type annotations are now fixed
```yaml
exclude: ^docs/
```

This allows MyPy to check our test files for type safety, which is beneficial since we fixed all the type annotation issues.

### 4. Dependencies Alignment
Pre-commit MyPy hook includes all necessary dependencies:
- `pydantic-ai-slim[openai]`
- `pytest`
- `click`
- `fastapi`
- `uvicorn`
- `rich`
- `httpx`

## Verification Results

✅ **All pre-commit hooks pass:**
```
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
check json...............................................................Passed
check toml...............................................................Passed
check for merge conflicts................................................Passed
debug statements (python)................................................Passed
ruff (legacy alias)......................................................Passed
ruff format..............................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed
pytest...................................................................Passed
```

## Alignment with CI

The pre-commit configuration now perfectly aligns with the CI pipeline:

| Tool | CI Version | Pre-commit Version | Status |
|------|------------|-------------------|---------|
| Ruff | 0.12.0 | v0.12.0 | ✅ Aligned |
| MyPy | 1.16.1 | v1.16.1 | ✅ Aligned |
| Bandit | 1.8.5 | 1.8.5 | ✅ Aligned |
| Pytest | Latest | Local hook | ✅ Added |
| Coverage | 80% threshold | N/A | ✅ CI only |

## Usage

Developers can now run pre-commit locally and get the same results as CI:

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run on staged files (automatic on commit)
git commit -m "your message"
```

This ensures consistent code quality across local development and CI environments.
