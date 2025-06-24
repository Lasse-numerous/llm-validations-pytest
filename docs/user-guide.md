# User Guide

pytest-LLM-Validate is a pytest plugin that enables **AI-driven qualitative testing** using Large Language Models (LLMs). Instead of writing complex assertions for subjective qualities like "user-friendly", "professional tone", or "appropriate response", you can describe your expectations in natural language and let an LLM evaluate whether your code meets those criteria.

## Why Use pytest-LLM-Validate?

Traditional testing excels at verifying exact outputs, but struggles with subjective qualities:

```python
# Traditional testing - exact match
def test_greeting():
    result = greet("Alice")
    assert result == "Hello, Alice!"  # Brittle, inflexible

# LLM testing - qualitative evaluation
@llm_eval("Should return a polite, personalized greeting")
def test_greeting():
    result = greet("Alice")
    return result  # Could be "Hi Alice!", "Hello there, Alice!", etc.
```

**Perfect for testing:**
- 🤖 AI/ML model outputs
- 📝 Generated text content
- 🎨 Creative algorithms
- 🗣️ Conversational interfaces
- 📧 Communication templates
- 🔄 Data transformations with subjective criteria

## Installation

### Requirements

- **Python**: 3.12+ (tested up to 3.13)
- **OpenAI API Key**: Required for LLM evaluations
- **pytest**: 6.0+ (installed automatically)

### Install Package

```bash
pip install pytest-llm-validate
```

### Configure API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Or create a `.env` file in your project root:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

### Verify Installation

```bash
pytest --version
# Should show pytest-llm-validate plugin loaded

python -c "from numerous.pytest_llm_validate import llm_eval; print('✓ Ready!')"
```

## Quick Start

### 1. Decorator API - Single Evaluation

Use `@llm_eval` to evaluate the return value of a test function:

```python
from numerous.pytest_llm_validate import llm_eval

@llm_eval("The function should return a polite greeting")
def test_greeting():
    def greet(name):
        return f"Hello, {name}!"

    return greet("World")  # LLM evaluates: "Hello, World!"
```

**What happens:**
1. Your test runs normally and returns `"Hello, World!"`
2. The LLM evaluates if this meets the specification "polite greeting"
3. If the LLM score is above the threshold (default 0.7), test passes
4. If below threshold, test fails with detailed LLM feedback

### 2. Fixture API - Multiple Evaluations

Use the `llm_eval` fixture for multiple checks within one test:

```python
def test_customer_service_responses(llm_eval):
    tester = llm_eval("All responses should be professional and helpful")

    # Test multiple scenarios
    complaint_response = handle_complaint("Product is broken")
    tester.check(complaint_response, label="complaint_handling")

    inquiry_response = handle_inquiry("What are your hours?")
    tester.check(inquiry_response, label="inquiry_response")

    # Get summary statistics
    summary = tester.get_summary()
    print(f"Passed: {summary['passed']}/{summary['total_checks']}")
```

## Core Concepts

### Specifications

Write clear, specific natural language descriptions:

```python
# ✅ Good specifications
@llm_eval("Response should be concise (under 50 words) and actionable")
@llm_eval("Generated code should follow PEP 8 style guidelines")
@llm_eval("Email should have professional tone and clear call-to-action")

# ❌ Vague specifications
@llm_eval("Should be good")
@llm_eval("Must work correctly")
```

### Thresholds

Control how strict the evaluation is (0.0 = always fail, 1.0 = always pass):

```python
@llm_eval("Extremely high quality required", threshold=0.9)  # Strict
@llm_eval("Basic quality check", threshold=0.5)             # Lenient
@llm_eval("Default quality", threshold=0.7)                 # Balanced (default)
```

### Models

Specify which LLM model to use:

```python
@llm_eval("...", model="gpt-4o-mini")      # Fast, cost-effective (default)
@llm_eval("...", model="gpt-4o")           # More capable, expensive
@llm_eval("...", model="gpt-3.5-turbo")    # Legacy option
```

### Evaluation Rules

Choose specialized evaluation rules for different contexts:

```python
@llm_eval("...", rule="general_quality")    # Overall code quality (default)
@llm_eval("...", rule="output_format")      # Formatting and structure
@llm_eval("...", rule="test_behavior")      # Test-specific behavior
```

## Advanced Usage

### Deduplication

Avoid redundant LLM calls by caching results (enabled by default):

```python
# These identical evaluations will only call LLM once
@llm_eval("Should be polite")
def test_greeting_1():
    return "Hello!"

@llm_eval("Should be polite")
def test_greeting_2():
    return "Hello!"  # Same spec + output = cached result

# Force fresh evaluation
@llm_eval("Should be polite", no_dedupe=True)
def test_greeting_fresh():
    return "Hello!"  # Always evaluates, never uses cache
```

### Metadata and Context

Provide additional context for better evaluations:

```python
@llm_eval(
    "Response should match the user's emotional tone",
    user_emotion="frustrated",
    context="customer_support"
)
def test_empathetic_response():
    return generate_response("I'm really upset about this delay!")
```

### Capture Outputs

The decorator captures multiple types of outputs:

```python
@llm_eval("Should provide helpful debugging info")
def test_debug_output():
    print("Debug: Processing started")  # Captured in 'stdout'
    logging.error("Connection failed")   # Captured in 'stderr'
    return {"status": "error", "details": "Network timeout"}  # 'return_value'
```

### Error Handling

Tests that raise exceptions are also evaluated:

```python
@llm_eval("Should raise a clear, helpful error message")
def test_validation_error():
    raise ValueError("Email address must contain @ symbol")
    # LLM evaluates the exception message for clarity
```

## Best Practices

### Writing Good Specifications

```python
# ✅ Specific and measurable
@llm_eval("Function should return a JSON object with 'name' and 'age' fields")

# ✅ Include quality criteria
@llm_eval("Error message should be user-friendly and suggest a solution")

# ✅ Specify format requirements
@llm_eval("Generated SQL should be properly formatted with table aliases")

# ❌ Too vague
@llm_eval("Should work well")

# ❌ Testing implementation details
@llm_eval("Should use a for loop")  # Test behavior, not implementation
```

### Organizing LLM Tests

```python
# Group related LLM tests in classes
class TestEmailGeneration:
    """LLM tests for email generation functionality."""

    @llm_eval("Welcome emails should be warm and professional")
    def test_welcome_email(self):
        return generate_welcome_email("John Doe")

    @llm_eval("Reminder emails should be polite but urgent")
    def test_reminder_email(self):
        return generate_reminder_email("Payment due")

# Use fixtures for common setup
@pytest.fixture
def email_generator():
    return EmailGenerator(template_dir="templates/")

def test_personalized_emails(llm_eval, email_generator):
    tester = llm_eval("All emails should include personalization")

    for user in ["Alice", "Bob", "Charlie"]:
        email = email_generator.create_welcome(user)
        tester.check(email, label=f"welcome_{user}")
```

### Performance Tips

1. **Use appropriate thresholds** - Lower thresholds for creative tasks, higher for precision tasks
2. **Leverage deduplication** - Group similar tests to benefit from caching
3. **Choose cost-effective models** - Use `gpt-4o-mini` for most cases
4. **Write focused specifications** - Specific specs get better LLM performance

### Testing Strategy

```python
# Combine traditional and LLM testing
def test_user_registration():
    # Traditional testing for exact behavior
    result = register_user("alice@example.com", "password123")
    assert result["success"] is True
    assert "user_id" in result

    # LLM testing for subjective qualities
    welcome_message = result["welcome_message"]
    tester = llm_eval("Welcome message should be friendly and informative")
    tester.check(welcome_message)
```

## Troubleshooting

### Common Issues

**"Plugin already registered" error:**
```bash
# Remove duplicate plugin registration
# Check tests/conftest.py for: pytest_plugins = [...]
```

**"API key not found" error:**
```bash
export OPENAI_API_KEY="your-key-here"
# Or check .env file in project root
```

**"LLM Evaluation Failed" with low score:**
- Review the LLM's comment for specific feedback
- Consider if your specification is too strict
- Lower the threshold if appropriate
- Improve your code to better match the specification

**Tests are slow:**
- Use `gpt-4o-mini` instead of `gpt-4o`
- Enable deduplication (default)
- Write more specific tests to reduce LLM processing time

### Debug Mode

Enable verbose output to see what's being evaluated:

```bash
pytest -v --tb=short
# Shows LLM specifications and scores

pytest -s
# Shows print statements and LLM feedback
```

## Next Steps

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Configuration Guide](configuration.md)** - Advanced configuration options
- **[Examples](examples.md)** - Real-world usage patterns
- **[Architecture](architecture.md)** - How pytest-LLM-Validate works internally
