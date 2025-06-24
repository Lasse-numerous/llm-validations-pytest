# API Reference

Complete reference for all pytest-LLM-Validate APIs, data models, and configuration options.

## Core APIs

### Decorator API

#### `@llm_eval(specification, *, threshold=0.7, model="gpt-4o-mini", rule=None, no_dedupe=False, **metadata)`

*Source: [`numerous/pytest_llm_validate/decorator.py:16`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/decorator.py#L16)*

Decorator for LLM-based evaluation of test outputs. The decorated function's return value, stdout, stderr, and any exceptions are captured and evaluated against the specification.

**Parameters:**

- **`specification`** (`str`): Natural language specification describing expected behavior
- **`threshold`** (`float`, default=`0.7`): Minimum score threshold for passing (0.0 to 1.0)
- **`model`** (`str`, default=`"gpt-4o-mini"`): LLM model to use for evaluation
- **`rule`** (`str | None`, default=`None`): Name of evaluation rule to use (defaults to 'general_quality')
- **`no_dedupe`** (`bool`, default=`False`): If True, skip deduplication and always perform fresh evaluation
- **`**metadata`** (`Any`): Additional metadata to include in the evaluation

**Returns:**
- `Callable`: Decorated test function that performs LLM evaluation

**Raises:**
- `AssertionError`: If the LLM evaluation fails to meet the threshold

**Examples:**

```python
# Basic usage
@llm_eval("The function should return a polite greeting")
def test_greeting():
    return greet("World")

# With custom threshold and model
@llm_eval("Response must be extremely professional", threshold=0.9, model="gpt-4o")
def test_professional_response():
    return generate_business_email()

# With metadata context
@llm_eval("Should match user's tone", user_emotion="excited", context="marketing")
def test_contextual_response():
    return create_marketing_copy()

# Skip deduplication for non-deterministic outputs
@llm_eval("Should be creative and unique", no_dedupe=True)
def test_creative_output():
    return generate_random_story()
```

**Captured Artifacts:**
- `return_value`: The function's return value
- `stdout`: Any printed output
- `stderr`: Any error output
- `exception`: Exception details if the function raises

### Fixture API

#### `llm_eval(specification, *, threshold=0.7, model="gpt-4o-mini", rule=None, no_dedupe=False, **metadata) -> LLMTester`

*Source: [`numerous/pytest_llm_validate/fixture.py:174`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py#L174)*

Pytest fixture that returns a factory function for creating `LLMTester` objects. Use this for multiple evaluations within a single test.

**Parameters:** Same as decorator API

**Returns:**
- `LLMTester`: Tester instance ready for performing checks

**Examples:**

```python
def test_multiple_outputs(llm_eval):
    tester = llm_eval("All outputs should be professional and helpful")

    tester.check("Thank you for contacting us.", label="greeting")
    tester.check("We'll resolve this promptly.", label="assurance")

    # Get evaluation summary
    summary = tester.get_summary()
    assert summary["passed"] == 2
```

### LLMTester Class

#### `class LLMTester`

*Source: [`numerous/pytest_llm_validate/fixture.py:12`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py#L12)*

Tester object for performing multiple LLM evaluations with shared configuration.

##### `__init__(specification, *, threshold=0.7, model="gpt-4o-mini", rule=None, no_dedupe=False, **metadata)`

Initialize the tester with evaluation parameters.

**Parameters:** Same as decorator and fixture APIs

##### `check(output, *, label=None, **check_metadata) -> None`

*Source: [`numerous/pytest_llm_validate/fixture.py:46`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py#L46)*

Perform a check on the given output.

**Parameters:**
- **`output`** (`Any`): The output to evaluate
- **`label`** (`str | None`): Optional label for this specific check
- **`**check_metadata`** (`Any`): Additional metadata for this specific check

**Raises:**
- `AssertionError`: If the evaluation fails to meet the threshold

**Example:**

```python
def test_email_responses(llm_eval):
    tester = llm_eval("Emails should be professional and empathetic")

    # Check different email types
    tester.check(apology_email(), label="apology", email_type="customer_service")
    tester.check(follow_up_email(), label="follow_up", priority="high")
```

##### `get_results() -> list[EvalResult]`

*Source: [`numerous/pytest_llm_validate/fixture.py:137`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py#L137)*

Get all evaluation results from checks performed so far.

**Returns:**
- `list[EvalResult]`: List of all evaluation results

##### `get_summary() -> dict[str, Any]`

*Source: [`numerous/pytest_llm_validate/fixture.py:140`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py#L140)*

Get summary statistics of all evaluations performed.

**Returns:**
- `dict[str, Any]`: Summary with keys:
  - `total_checks`: Total number of checks performed
  - `passed`: Number of checks that passed
  - `failed`: Number of checks that failed
  - `average_score`: Average score across all checks
  - `scores`: List of all scores

**Example:**

```python
def test_batch_evaluation(llm_eval):
    tester = llm_eval("All outputs should be high quality")

    for i in range(5):
        tester.check(f"Output {i}", label=f"test_{i}")

    summary = tester.get_summary()
    print(f"Success rate: {summary['passed']}/{summary['total_checks']}")
    print(f"Average score: {summary['average_score']:.2f}")
```

## Data Models

### EvalRule

*Source: [`numerous/pytest_llm_validate/models.py:8`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/models.py#L8)*

A rule containing prompts and configuration for LLM evaluation.

**Fields:**
- **`name`** (`str`): Unique identifier for the rule
- **`description`** (`str`): Human-readable description of what this rule evaluates
- **`prompt`** (`str`): The actual LLM prompt template
- **`version`** (`str`, default=`"1.0"`): Version of the rule
- **`author`** (`str`, default=`"pytest-llm-validate"`): Author of the rule
- **`tags`** (`list[str]`, default=`[]`): Tags for categorizing rules

**Example:**

```python
from numerous.pytest_llm_validate.models import EvalRule

rule = EvalRule(
    name="code_quality",
    description="Evaluates code quality and best practices",
    prompt="Evaluate the code for quality, readability, and best practices...",
    tags=["code", "quality", "best-practices"]
)
```

### EvalRequest

*Source: [`numerous/pytest_llm_validate/models.py:23`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/models.py#L23)*

Request structure for LLM evaluation.

**Fields:**
- **`specification`** (`str`): Natural language specification from user
- **`artifacts`** (`dict[str, Any]`): Code outputs to evaluate
- **`rule`** (`EvalRule`): Rule to use for evaluation
- **`threshold`** (`float`, default=`0.7`): Minimum score threshold for passing
- **`model`** (`str`, default=`"gpt-4o-mini"`): LLM model to use
- **`metadata`** (`dict[str, Any]`, default=`{}`): Additional metadata

### EvalResult

*Source: [`numerous/pytest_llm_validate/models.py:38`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/models.py#L38)*

Result structure from LLM evaluation.

**Fields:**
- **`score`** (`float`): Numerical score between 0.0 and 1.0
- **`comment`** (`str`): Detailed explanation from the LLM
- **`passed`** (`bool`): Whether the evaluation passed the threshold
- **`request`** (`EvalRequest`): Original request that generated this result
- **`model_used`** (`str`): Actual model used for evaluation
- **`timestamp`** (`str`): ISO timestamp of evaluation

**Properties:**

##### `passed_threshold -> bool`

*Source: [`numerous/pytest_llm_validate/models.py:53`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/models.py#L53)*

Check if score meets the threshold requirement.

## Built-in Evaluation Rules

### general_quality

*Source: [`numerous/pytest_llm_validate/rules/general_quality.mdc`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/rules/general_quality.mdc)*

Default rule for overall code quality evaluation.

**Evaluation Criteria:**
- **Correctness** (40%): Does the output correctly implement what was specified?
- **Quality** (30%): Is the code well-structured, readable, and following best practices?
- **Completeness** (20%): Does the output fully address all aspects of the specification?
- **Appropriateness** (10%): Is the output appropriate for the given context?

**Usage:**
```python
@llm_eval("Should be high quality", rule="general_quality")  # Default
```

### output_format

*Source: [`numerous/pytest_llm_validate/rules/output_format.mdc`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/rules/output_format.mdc)*

Specialized rule for evaluating output formatting and structure.

**Usage:**
```python
@llm_eval("Should be properly formatted JSON", rule="output_format")
```

### test_behavior

*Source: [`numerous/pytest_llm_validate/rules/test_behavior.mdc`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/rules/test_behavior.mdc)*

Rule for evaluating test-specific behavior and assertions.

**Usage:**
```python
@llm_eval("Test should validate edge cases", rule="test_behavior")
```

## Advanced APIs

### Agent System

#### `get_agent() -> EvalAgent`

*Source: [`numerous/pytest_llm_validate/agent.py:155`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/agent.py#L155)*

Get the singleton LLM evaluation agent.

**Returns:**
- `EvalAgent`: Configured agent for performing evaluations

#### `class EvalAgent`

*Source: [`numerous/pytest_llm_validate/agent.py:14`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/agent.py#L14)*

Agent for performing LLM-based evaluations using PydanticAI.

##### `async evaluate(request: EvalRequest) -> EvalResult`

*Source: [`numerous/pytest_llm_validate/agent.py:41`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/agent.py#L41)*

Evaluate a request using the LLM agent.

**Parameters:**
- **`request`** (`EvalRequest`): Evaluation request with specification and artifacts

**Returns:**
- `EvalResult`: Evaluation result with score, comment, and pass/fail status

### History and Caching

#### `get_history() -> EvalHistory`

*Source: [`numerous/pytest_llm_validate/history.py:200`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/history.py#L200)*

Get the singleton evaluation history manager.

**Returns:**
- `EvalHistory`: History manager for caching and deduplication

#### `class EvalHistory`

*Source: [`numerous/pytest_llm_validate/history.py:18`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/history.py#L18)*

Manages evaluation history and caching for deduplication.

##### `get_cached_result(request: EvalRequest) -> EvalResult | None`

Check if a cached result exists for the given request.

##### `cache_result(result: EvalResult) -> None`

Cache an evaluation result for future deduplication.

### Rule Loading

#### `get_rule(name: str) -> EvalRule | None`

*Source: [`numerous/pytest_llm_validate/loader.py:21`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/loader.py#L21)*

Load a specific evaluation rule by name.

**Parameters:**
- **`name`** (`str`): Name of the rule to load

**Returns:**
- `EvalRule | None`: The loaded rule, or None if not found

#### `get_default_rule() -> EvalRule`

*Source: [`numerous/pytest_llm_validate/loader.py:32`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/loader.py#L32)*

Get the default evaluation rule (general_quality).

**Returns:**
- `EvalRule`: Default rule for general quality evaluation

#### `list_available_rules() -> list[str]`

*Source: [`numerous/pytest_llm_validate/loader.py:43`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/loader.py#L43)*

List all available evaluation rules.

**Returns:**
- `list[str]`: Names of all available rules

## Configuration

### Environment Variables

- **`OPENAI_API_KEY`**: Required. Your OpenAI API key for LLM access
- **`PYTEST_LLM_VALIDATE_MODEL`**: Default model to use (default: "gpt-4o-mini")
- **`PYTEST_LLM_VALIDATE_THRESHOLD`**: Default threshold (default: 0.7)
- **`PYTEST_LLM_VALIDATE_CACHE_DIR`**: Directory for evaluation cache (default: ".pytest-llm-validate-cache")

### Pytest Configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# Disable LLM tests by default (enable with --llm)
addopts = ["-m", "not llm"]

# Mark LLM tests
markers = [
    "llm: marks tests as requiring LLM evaluation (deselect with '-m \"not llm\"')",
]
```

Add to `pytest.ini`:

```ini
[pytest]
# Disable LLM tests by default
addopts = -m "not llm"

# Mark LLM tests
markers =
    llm: marks tests as requiring LLM evaluation
```

### Test Marking

Mark tests that use LLM evaluation:

```python
import pytest

@pytest.mark.llm
@llm_eval("Should be professional")
def test_with_llm():
    return "Hello, World!"

# Run only LLM tests
# pytest -m llm

# Skip LLM tests
# pytest -m "not llm"
```

## Error Handling

### AssertionError Format

When an LLM evaluation fails, pytest-LLM-Validate raises an `AssertionError` with detailed information:

```
AssertionError: LLM Evaluation Failed (score: 0.45, threshold: 0.70)
Specification: The response should be professional and helpful
Output: sup dude, dunno what you want
LLM Feedback: The response is too casual and doesn't provide helpful information.
It uses informal language ("sup dude") and dismissive tone ("dunno") which doesn't
meet professional standards.
```

### Exception Handling

The library handles various error conditions gracefully:

- **API errors**: Fallback evaluation with error details
- **Network timeouts**: Retry logic with exponential backoff
- **Invalid responses**: Parsing fallbacks and error recovery
- **Configuration errors**: Clear error messages with suggestions

## Performance Considerations

### Cost Optimization

- **Model selection**: Use `gpt-4o-mini` (default) for cost-effectiveness
- **Deduplication**: Enabled by default to avoid redundant evaluations
- **Batching**: Group similar evaluations to benefit from caching

### Speed Optimization

- **Async evaluation**: All LLM calls are asynchronous under the hood
- **Caching**: Results are cached by content hash for instant retrieval
- **Parallel execution**: Multiple tests can run LLM evaluations concurrently

### Resource Usage

- **Memory**: Evaluation cache is memory-efficient with LRU eviction
- **Storage**: Persistent cache stored in `.pytest-llm-validate-cache/`
- **Network**: Only unique evaluations result in API calls

## Integration Examples

### CI/CD Integration

```yaml
# GitHub Actions example
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - run: pip install pytest-llm-validate
      - run: pytest -m "not llm"  # Skip LLM tests in CI by default
      - run: pytest -m llm       # Run LLM tests separately
```

### Custom Rules

Create custom evaluation rules by adding `.mdc` files to your project:

```markdown
<!-- custom_rules/api_documentation.mdc -->
**Author:** my-team
**Tags:** api, documentation, completeness

## Evaluation Prompt

Evaluate API documentation for completeness and clarity.

### Criteria
1. **Completeness** (40%): All endpoints documented
2. **Clarity** (30%): Clear descriptions and examples
3. **Accuracy** (20%): Correct parameter types and responses
4. **Usability** (10%): Easy to follow and understand

### Response Format
```json
{
  "score": 0.85,
  "comment": "Documentation is comprehensive but could use more examples..."
}
```
```

Then use it in tests:

```python
@llm_eval("API docs should be complete and clear", rule="api_documentation")
def test_api_documentation():
    return generate_api_docs()
```
