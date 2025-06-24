# pytest-LLM-Validate Documentation

A pytest plugin that enables **AI-driven qualitative testing** using Large Language Models (LLMs) for evaluating subjective qualities like "user-friendly", "professional tone", or "appropriate response" that are difficult to validate with traditional assertions.

## Overview

pytest-LLM-Validate provides two intuitive APIs for incorporating LLM evaluations into your test suite:

- **🎯 Decorator API** - `@llm_eval` for single evaluations
- **🔄 Fixture API** - `llm_eval` fixture for multiple evaluations within one test
- **📊 Built-in Reporting** - Rich output with scores and LLM feedback
- **⚡ Smart Caching** - Deduplication to avoid redundant LLM calls
- **🛡️ Production Ready** - Robust error handling and CI/CD integration

## Quick Start

### Installation & Setup

```bash
pip install pytest-llm-validate
export OPENAI_API_KEY="sk-proj-..."
```

### Basic Usage

```python
from numerous.pytest_llm_validate import llm_eval

# Decorator API - Single evaluation
@llm_eval("The function should return a polite greeting")
def test_greeting():
    result = greet("Alice")
    return result  # LLM evaluates: "Hello, Alice!"

# Fixture API - Multiple evaluations
def test_customer_responses(llm_eval):
    tester = llm_eval("All responses should be professional and helpful")

    tester.check("Thank you for contacting us.", label="greeting")
    tester.check("We'll resolve this promptly.", label="assurance")

    summary = tester.get_summary()
    assert summary["passed"] == 2
```

## Documentation Sections

### 📖 **Getting Started**

- **[User Guide](user-guide.md)** - Complete introduction with installation, concepts, and best practices
- **[Examples & Tutorials](examples.md)** - Real-world usage patterns from basic to advanced scenarios
- **[Configuration Guide](configuration.md)** - Environment setup, pytest integration, and advanced configuration

### 🔧 **Technical Reference**

- **[API Reference](api-reference.md)** - Complete API documentation with links to source code
- **[Architecture](architecture.md)** - Internal architecture and design decisions
- **[Contributing Guide](https://github.com/numerous-com/pytest-llm-validate/blob/main/CONTRIBUTING.md)** - Development workflow and contribution guidelines

### 🚀 **Project Information**

- **[Product Requirements](product-requirements.md)** - Complete product specification and development roadmap
- **[Developer Workflow](developer-workflow.md)** - Development processes, testing standards, and CI/CD
- **[CI Debugging Guide](ci-debugging.md)** - Troubleshooting CI issues and enhanced pre-push validation

## Core Features

### 🎯 **Flexible Evaluation APIs**

Choose the approach that fits your testing needs:

```python
# Decorator for single evaluations
@llm_eval("Should be user-friendly and clear")
def test_ui_message():
    return generate_welcome_message()

# Fixture for multiple related checks
def test_email_campaign(llm_eval):
    tester = llm_eval("All emails should be professional and engaging")

    for template in ["welcome", "reminder", "follow_up"]:
        email = generate_email(template)
        tester.check(email, label=template)
```

### 📊 **Built-in Evaluation Rules**

Specialized rules for different domains:

- **`general_quality`** - Overall code/content quality (default)
- **`output_format`** - Structure and formatting evaluation
- **`test_behavior`** - Test-specific behavior validation

```python
@llm_eval("API response should be properly formatted", rule="output_format")
def test_api_response_format():
    return {"status": "success", "data": {...}}
```

### ⚡ **Smart Performance Features**

- **Deduplication** - Identical evaluations use cached results
- **Async Processing** - Non-blocking LLM calls
- **Cost Optimization** - Configurable models and thresholds
- **Batch Processing** - Efficient handling of multiple evaluations

### 🛡️ **Production-Ready Features**

- **Robust Error Handling** - Graceful degradation on API failures
- **CI/CD Integration** - Skip LLM tests in CI, run separately
- **Comprehensive Logging** - Debug modes and performance tracking
- **Configuration Management** - Environment-specific settings

## Use Cases

### 🤖 **AI/ML Testing**

Perfect for testing AI-generated content, model outputs, and ML pipeline results:

```python
@llm_eval("Generated code should follow Python best practices")
def test_ai_code_generation():
    prompt = "Create a function to validate email addresses"
    return ai_code_generator.generate(prompt)

def test_chatbot_responses(llm_eval):
    tester = llm_eval("Responses should be helpful and empathetic")

    for scenario in customer_scenarios:
        response = chatbot.respond(scenario)
        tester.check(response, label=scenario.type)
```

### 📝 **Content Quality Assurance**

Validate generated text, documentation, and user-facing content:

```python
@llm_eval("Documentation should be comprehensive and beginner-friendly")
def test_api_documentation():
    return generate_api_docs(endpoints)

@llm_eval("Error messages should be helpful and suggest solutions")
def test_error_handling():
    try:
        invalid_operation()
    except Exception as e:
        return format_user_error(e)
```

### 🔄 **Data Pipeline Validation**

Ensure data transformations produce quality, consistent outputs:

```python
def test_data_processing_quality(llm_eval):
    tester = llm_eval("Processed data should be clean and well-structured")

    raw_data = load_sample_data()
    processed = data_pipeline.transform(raw_data)

    tester.check(processed, label="data_transformation")
```

## Advanced Features

### 🎛️ **Customizable Configuration**

Fine-tune evaluation behavior for your specific needs:

```python
@llm_eval(
    "Response should match customer's emotional tone",
    threshold=0.8,           # Higher quality requirement
    model="gpt-4o",          # Premium model for critical content
    user_emotion="frustrated", # Additional context
    no_dedupe=True           # Always fresh evaluation
)
def test_empathetic_response():
    return customer_service.respond_to_complaint()
```

### 🏗️ **Custom Evaluation Rules**

Create domain-specific rules for specialized evaluation criteria:

```python
# custom_rules/security_review.mdc
@llm_eval(
    "Code should be secure and follow security best practices",
    rule="security_review",  # Custom security-focused rule
    threshold=0.95           # Very high threshold for security
)
def test_secure_authentication():
    return generate_auth_code()
```

### 📈 **Performance Monitoring**

Track API usage, costs, and evaluation performance:

```python
def test_batch_processing(llm_eval):
    tester = llm_eval("Content should maintain quality under load")

    # Process large batches efficiently
    for batch in process_content_batches():
        for item in batch:
            tester.check(item.content, label=f"batch_{item.id}")

    # Analyze performance
    summary = tester.get_summary()
    print(f"Processed {summary['total_checks']} items")
    print(f"Average quality: {summary['average_score']:.2f}")
```

## Integration Examples

### 🔄 **CI/CD Pipeline**

Seamlessly integrate with your existing CI/CD workflows:

```yaml
# GitHub Actions
- name: Run traditional tests
  run: pytest -m "not llm"

- name: Run LLM quality tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: pytest -m llm --llm-model="gpt-4o-mini"
```

### 🌐 **Web Application Testing**

Test user-facing content and error handling:

```python
@llm_eval("Error pages should be user-friendly and helpful")
def test_404_page():
    response = client.get('/nonexistent-page/')
    return response.content.decode()

def test_form_validation_messages(llm_eval):
    tester = llm_eval("Validation messages should be clear and actionable")

    invalid_inputs = ["invalid-email", "", "password123"]
    for input_data in invalid_inputs:
        response = submit_form(input_data)
        tester.check(response.error_message, label=f"error_{input_data}")
```

## Getting Help

### 📚 **Documentation**

- Browse the **[Complete Documentation](user-guide.md)** for detailed guides
- Check **[API Reference](api-reference.md)** for technical details
- Explore **[Examples](examples.md)** for real-world usage patterns

### 🐛 **Troubleshooting**

- Review **[Configuration Guide](configuration.md)** for setup issues
- Check **[CI Debugging Guide](ci-debugging.md)** for CI/CD problems
- Enable debug mode: `pytest --llm-debug -v -s`

### 🤝 **Community**

- **Issues & Feature Requests** - [GitHub Issues](https://github.com/numerous-com/pytest-llm-validate/issues)
- **Contributions** - See [Contributing Guide](https://github.com/numerous-com/pytest-llm-validate/blob/main/CONTRIBUTING.md)
- **Development** - Follow [Developer Workflow](developer-workflow.md)

## What's Next?

1. **[Install and configure](user-guide.md#installation)** pytest-LLM-Validate
2. **[Try the examples](examples.md)** to understand the patterns
3. **[Configure for your environment](configuration.md)** with proper settings
4. **[Explore the API](api-reference.md)** for advanced usage
5. **[Contribute](https://github.com/numerous-com/pytest-llm-validate/blob/main/CONTRIBUTING.md)** to the project development

---

**Ready to start testing qualitative aspects of your code with AI?**

👉 **[Get Started with the User Guide](user-guide.md)**
