# Configuration Guide

Complete configuration reference for pytest-LLM-Validate covering environment setup, pytest integration, and advanced configuration options.

## Environment Setup

### OpenAI API Configuration

#### Required: API Key

Set your OpenAI API key using one of these methods:

**Environment Variable (Recommended):**
```bash
export OPENAI_API_KEY="sk-proj-..."
```

**`.env` File:**
```bash
# .env file in project root
OPENAI_API_KEY=sk-proj-...
```

**System Environment (Windows):**
```cmd
set OPENAI_API_KEY=sk-proj-...
```

#### Optional: API Configuration

```bash
# Override default model
export PYTEST_LLM_VALIDATE_MODEL="gpt-4o"

# Set default threshold
export PYTEST_LLM_VALIDATE_THRESHOLD="0.8"

# Configure API timeout (seconds)
export OPENAI_TIMEOUT="30"

# Use different OpenAI base URL (for proxies/alternatives)
export OPENAI_BASE_URL="https://your-proxy.com/v1"
```

### Cache Configuration

```bash
# Cache directory location
export PYTEST_LLM_VALIDATE_CACHE_DIR=".pytest-llm-cache"

# Disable caching entirely (not recommended)
export PYTEST_LLM_VALIDATE_DISABLE_CACHE="true"

# Cache TTL in hours (default: 24)
export PYTEST_LLM_VALIDATE_CACHE_TTL="48"

# Maximum cache size in MB (default: 100)
export PYTEST_LLM_VALIDATE_CACHE_SIZE="200"
```

## Pytest Integration

### Configuration Files

#### `pyproject.toml` Configuration

```toml
[tool.pytest.ini_options]
# Basic pytest-llm-validate configuration
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra"
]

# Test markers
markers = [
    "llm: marks tests as requiring LLM evaluation (deselect with '-m \"not llm\"')",
    "slow: marks tests as slow running",
    "integration: marks tests as integration tests"
]

# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Filtering (disable LLM tests by default in CI)
addopts = ["-m", "not llm"]

[tool.pytest-llm-validate]
# Plugin-specific configuration
default_model = "gpt-4o-mini"
default_threshold = 0.7
cache_enabled = true
cache_dir = ".pytest-llm-validate-cache"
verbose_failures = true

# Rule configuration
rules_dir = "custom_rules"  # Additional custom rules directory
default_rule = "general_quality"

# Cost management
max_api_calls_per_test = 10
warn_on_high_usage = true
cost_tracking = true
```

#### `pytest.ini` Configuration

```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    llm: marks tests as requiring LLM evaluation
    slow: marks tests as slow running
    integration: marks tests as integration tests

# Default options
addopts =
    --strict-markers
    --strict-config
    -ra
    -m "not llm"

# Plugin configuration
llm_validate_model = gpt-4o-mini
llm_validate_threshold = 0.7
llm_validate_cache_dir = .pytest-llm-validate-cache
```

#### `setup.cfg` Configuration (Legacy)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    llm: LLM evaluation tests
    slow: slow running tests

addopts =
    --strict-markers
    -m "not llm"

[pytest-llm-validate]
default_model = gpt-4o-mini
default_threshold = 0.7
cache_enabled = true
```

### Test Execution Control

#### Running Tests

```bash
# Run all tests except LLM tests (default)
pytest

# Run only LLM tests
pytest -m llm

# Run all tests including LLM tests
pytest -m ""

# Run with verbose LLM output
pytest -m llm -v -s

# Run specific LLM test files
pytest tests/test_llm_*.py

# Run with custom model
pytest -m llm --llm-model="gpt-4o"

# Run with custom threshold
pytest -m llm --llm-threshold=0.8
```

#### CI/CD Configuration

**GitHub Actions:**
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run standard tests
        run: pytest -m "not llm"

      - name: Run LLM tests
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: pytest -m llm --llm-model="gpt-4o-mini"
```

**GitLab CI:**
```yaml
stages:
  - test
  - llm-test

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

test:
  stage: test
  script:
    - pip install -e ".[dev]"
    - pytest -m "not llm"
  cache:
    paths:
      - .cache/pip

llm-test:
  stage: llm-test
  script:
    - pip install -e ".[dev]"
    - pytest -m llm
  only:
    - main
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
```

## Advanced Configuration

### Custom Rules

#### Creating Custom Rules

Create `.mdc` files in your project:

```
project/
├── custom_rules/
│   ├── __init__.py
│   ├── security_review.mdc
│   ├── performance_check.mdc
│   └── accessibility_audit.mdc
├── tests/
└── pyproject.toml
```

**Example Custom Rule (`custom_rules/security_review.mdc`):**

```markdown
**Author:** security-team
**Tags:** security, vulnerability, code-review

## Evaluation Prompt

You are a cybersecurity expert reviewing code for potential security vulnerabilities.

### Input Context
- **Security Specification:** {{specification}}
- **Code/Output:** {{artifacts}}

### Security Checklist

Evaluate the code against these security criteria:

1. **Input Validation** (25%): Proper validation and sanitization
2. **Authentication/Authorization** (25%): Correct access controls
3. **Data Protection** (20%): Sensitive data handling
4. **Error Handling** (15%): No information leakage
5. **Best Practices** (15%): Following security guidelines

### Response Format

```json
{
  "score": 0.85,
  "comment": "Detailed security assessment with specific recommendations for any vulnerabilities found."
}
```

**Important:**
- Flag any potential security issues immediately
- Provide specific remediation steps
- Consider OWASP Top 10 vulnerabilities
```

#### Using Custom Rules

```python
from numerous.pytest_llm_validate import llm_eval

@llm_eval(
    "Code should be secure and follow security best practices",
    rule="security_review",
    threshold=0.9  # High threshold for security
)
def test_secure_authentication():
    return generate_auth_code()
```

#### Rule Loading Configuration

```python
# conftest.py
import pytest
from numerous.pytest_llm_validate.loader import register_rule_directory

def pytest_configure(config):
    """Register custom rule directories."""
    register_rule_directory("custom_rules")
    register_rule_directory("domain_specific_rules")
```

### Model Configuration

#### Model Selection Strategy

```python
# conftest.py
import os
import pytest

def pytest_configure(config):
    """Configure model selection based on environment."""
    if os.getenv("CI"):
        # Use cost-effective model in CI
        os.environ.setdefault("PYTEST_LLM_VALIDATE_MODEL", "gpt-4o-mini")
    elif os.getenv("PRODUCTION_TESTS"):
        # Use high-quality model for production validation
        os.environ.setdefault("PYTEST_LLM_VALIDATE_MODEL", "gpt-4o")
    else:
        # Default for development
        os.environ.setdefault("PYTEST_LLM_VALIDATE_MODEL", "gpt-4o-mini")
```

#### Dynamic Model Selection

```python
def test_critical_content(llm_eval):
    """Use different models for different criticality levels."""

    # High-stakes content gets premium model
    critical_tester = llm_eval(
        "Legal content must be accurate and compliant",
        model="gpt-4o",
        threshold=0.95
    )

    # Standard content uses default model
    standard_tester = llm_eval(
        "Content should be professional and clear",
        model="gpt-4o-mini",
        threshold=0.7
    )

    critical_content = generate_legal_disclaimer()
    critical_tester.check(critical_content)

    standard_content = generate_blog_post()
    standard_tester.check(standard_content)
```

### Performance Configuration

#### Concurrency Control

```python
# conftest.py
import asyncio
import pytest

@pytest.fixture(scope="session", autouse=True)
def configure_async():
    """Configure async behavior for LLM calls."""
    # Limit concurrent LLM requests
    semaphore = asyncio.Semaphore(5)

    # Set custom event loop policy if needed
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

#### Cost Management

```python
# conftest.py
import pytest
from collections import defaultdict

# Track API usage
api_usage_tracker = defaultdict(int)

@pytest.fixture(autouse=True)
def track_api_usage(request):
    """Track API usage per test."""
    test_name = request.node.name

    # Pre-test: record starting usage
    starting_calls = get_current_api_calls()

    yield

    # Post-test: calculate usage
    ending_calls = get_current_api_calls()
    usage = ending_calls - starting_calls
    api_usage_tracker[test_name] = usage

    # Warn on high usage
    if usage > 10:
        pytest.warn(f"Test {test_name} made {usage} API calls")

def pytest_sessionfinish(session, exitstatus):
    """Report API usage summary."""
    total_calls = sum(api_usage_tracker.values())
    print(f"\nTotal API calls: {total_calls}")

    # Show top consumers
    top_tests = sorted(api_usage_tracker.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Top API consumers:")
    for test, calls in top_tests:
        print(f"  {test}: {calls} calls")
```

#### Caching Strategy

```python
# conftest.py
import pytest
from numerous.pytest_llm_validate.history import get_history

@pytest.fixture(scope="session", autouse=True)
def configure_caching():
    """Configure caching behavior."""
    history = get_history()

    # Pre-load common evaluations
    common_specs = [
        "Should be professional and polite",
        "Should be clear and concise",
        "Should follow best practices"
    ]

    # Optionally pre-warm cache with common patterns
    # history.preload_common_patterns(common_specs)

def pytest_configure(config):
    """Configure cache settings."""
    import os

    # Environment-specific cache configuration
    if config.getoption("--cache-clear"):
        # Clear cache when requested
        os.environ["PYTEST_LLM_VALIDATE_DISABLE_CACHE"] = "true"

    if os.getenv("CI"):
        # Shorter TTL in CI
        os.environ["PYTEST_LLM_VALIDATE_CACHE_TTL"] = "1"
```

### Error Handling Configuration

#### Custom Error Handlers

```python
# conftest.py
import pytest
from numerous.pytest_llm_validate.agent import get_agent

@pytest.fixture(autouse=True)
def configure_error_handling():
    """Configure custom error handling."""
    agent = get_agent()

    # Custom retry configuration
    agent.max_retries = 3
    agent.retry_delay = 1.0

    # Custom error handlers
    def handle_rate_limit(error):
        pytest.skip(f"Rate limited: {error}")

    def handle_api_error(error):
        pytest.fail(f"API error: {error}")

    agent.register_error_handler("rate_limit", handle_rate_limit)
    agent.register_error_handler("api_error", handle_api_error)
```

#### Graceful Degradation

```python
# conftest.py
import pytest
import os

def pytest_runtest_setup(item):
    """Skip LLM tests if API key is not available."""
    if item.get_closest_marker("llm"):
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not configured")

        # Check API connectivity
        try:
            from numerous.pytest_llm_validate.agent import get_agent
            agent = get_agent()
            # Quick connectivity test
            # agent.test_connection()
        except Exception as e:
            pytest.skip(f"LLM service unavailable: {e}")
```

## Environment-Specific Configuration

### Development Environment

```bash
# .env.development
OPENAI_API_KEY=sk-proj-dev-key
PYTEST_LLM_VALIDATE_MODEL=gpt-4o-mini
PYTEST_LLM_VALIDATE_THRESHOLD=0.6  # Lower threshold for development
PYTEST_LLM_VALIDATE_CACHE_TTL=168  # 1 week cache
```

### Testing Environment

```bash
# .env.testing
OPENAI_API_KEY=sk-proj-test-key
PYTEST_LLM_VALIDATE_MODEL=gpt-4o-mini
PYTEST_LLM_VALIDATE_THRESHOLD=0.7
PYTEST_LLM_VALIDATE_CACHE_TTL=24   # 1 day cache
```

### Production Environment

```bash
# .env.production
OPENAI_API_KEY=sk-proj-prod-key
PYTEST_LLM_VALIDATE_MODEL=gpt-4o    # Higher quality model
PYTEST_LLM_VALIDATE_THRESHOLD=0.9   # Strict quality requirements
PYTEST_LLM_VALIDATE_CACHE_TTL=72    # 3 day cache
```

## Troubleshooting Configuration

### Debug Configuration

```python
# conftest.py
import logging
import pytest

def pytest_configure(config):
    """Configure debugging."""
    if config.getoption("--llm-debug"):
        # Enable detailed logging
        logging.getLogger("numerous.pytest_llm_validate").setLevel(logging.DEBUG)

        # Enable API request/response logging
        logging.getLogger("openai").setLevel(logging.DEBUG)

        # Enable cache debugging
        logging.getLogger("llm_cache").setLevel(logging.DEBUG)

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--llm-debug",
        action="store_true",
        default=False,
        help="Enable LLM debugging output"
    )

    parser.addoption(
        "--llm-model",
        action="store",
        default=None,
        help="Override default LLM model"
    )

    parser.addoption(
        "--llm-threshold",
        action="store",
        type=float,
        default=None,
        help="Override default threshold"
    )
```

### Common Configuration Issues

#### Issue: Plugin Not Loading

**Solution:**
```python
# setup.py or pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project"
dependencies = [
    "pytest-llm-validate>=0.1.0"
]

[project.entry-points.pytest11]
llm_validate = "numerous.pytest_llm_validate.plugin"
```

#### Issue: API Key Not Found

**Solution:**
```python
# conftest.py
import os
import pytest

def pytest_configure(config):
    """Ensure API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        # Try loading from different sources
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        if not os.getenv("OPENAI_API_KEY"):
            pytest.exit("OPENAI_API_KEY environment variable is required")
```

#### Issue: Tests Too Slow

**Solution:**
```python
# conftest.py
import pytest

def pytest_configure(config):
    """Optimize for speed."""
    import os

    # Use faster model
    os.environ.setdefault("PYTEST_LLM_VALIDATE_MODEL", "gpt-4o-mini")

    # Enable aggressive caching
    os.environ.setdefault("PYTEST_LLM_VALIDATE_CACHE_TTL", "168")  # 1 week

    # Reduce timeout for faster failures
    os.environ.setdefault("OPENAI_TIMEOUT", "10")
```

This configuration guide provides comprehensive coverage of all setup options, from basic environment configuration to advanced performance tuning and troubleshooting.
