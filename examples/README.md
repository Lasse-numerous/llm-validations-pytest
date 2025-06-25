# pytest-LLM-Validate Examples

This directory contains runnable examples demonstrating how to use the pytest-LLM-Validate plugin for AI-driven qualitative testing.

## Prerequisites

1. **Install the plugin:**
   ```bash
   pip install pytest-llm-validate
   # or for development:
   pip install -e ".[dev]"
   ```

2. **Set up your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Examples

### 1. Simple Example (`simple_example.py`)

Demonstrates the basic usage of both APIs:
- **Decorator API**: Using `@llm_eval` to validate function outputs
- **Fixture API**: Using `llm_eval` fixture for multiple checks

```bash
pytest examples/simple_example.py -v
```

**What it shows:**
- Basic greeting function validation
- Email response quality assessment
- Multiple response testing with labels

### 2. Advanced Example (`advanced_example.py`)

Shows more sophisticated usage patterns:
- Custom thresholds and model selection
- Code quality evaluation
- API response validation
- Structured testing approaches

```bash
pytest examples/advanced_example.py -v
```

**What it shows:**
- Higher thresholds for critical assessments
- Source code quality evaluation
- API response structure and content validation
- Multiple evaluation criteria per test

## Running All Examples

```bash
# Run all examples
pytest examples/ -v

# Run with more verbose output
pytest examples/ -v -s

# Run specific example
pytest examples/simple_example.py::test_greeting -v
```

## Common Usage Patterns

### Decorator API
```python
@llm_eval("The output should be professional and helpful")
def test_my_function():
    result = my_function("input")
    return result  # This gets evaluated by the LLM
```

### Fixture API
```python
def test_multiple_outputs(llm_eval):
    tester = llm_eval("All outputs should meet quality standards")
    
    result1 = generate_output("scenario1")
    tester.check(result1, label="scenario1")
    
    result2 = generate_output("scenario2") 
    tester.check(result2, label="scenario2")
```

### Custom Configuration
```python
@llm_eval(
    "Specification text",
    threshold=0.8,           # Higher threshold (0.0-1.0)
    model="gpt-4o-mini",     # Specify model
    rule="custom_rule",      # Use custom evaluation rule
    project="my_project"     # Add metadata
)
```

## Tips for Writing Good Tests

1. **Clear Specifications**: Write specific, actionable criteria
   - ✅ "The response should be polite and include next steps"
   - ❌ "The response should be good"

2. **Appropriate Thresholds**: 
   - Use 0.6-0.7 for general quality checks
   - Use 0.8+ for critical functionality
   - Use 0.5 for experimental features

3. **Meaningful Labels**: Use descriptive labels for fixture API checks
   ```python
   tester.check(result, label="error_handling_scenario")
   ```

4. **Test Realistic Outputs**: Use real-world examples and edge cases

## Troubleshooting

- **API Key Issues**: Ensure `OPENAI_API_KEY` is set correctly
- **Import Errors**: Verify the plugin is installed properly
- **Rate Limiting**: The plugin includes deduplication to minimize API calls
- **Timeout Issues**: Try reducing the complexity of outputs being evaluated

For more information, see the [main documentation](../README.md). 