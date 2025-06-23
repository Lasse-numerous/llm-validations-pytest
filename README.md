# pytest-LLM-Validate

**`pytest-LLM-Validate` is a pytest plugin and toolkit that lets developers embed AI-driven qualitative & behavioural tests into their codebase with minimal boilerplate.**

This project aims to empower Python developers to validate live code outputs against natural-language criteria using simple and intuitive APIs. It leverages PydanticAI for interactions with Large Language Models (LLMs), initially targeting OpenAI's `o4-mini`.

## Key Features (Planned)

*   **Natural Language Test Specifications**: Write your test expectations in plain English.
*   **Decorator API**: Easily annotate your existing test functions with `@llm_eval` to specify criteria and have their return values (or stdout/stderr) evaluated.
*   **Fixture API**: For more complex scenarios, use the `llm_eval()` fixture to get a tester object and perform multiple checks within a single test.
*   **Packaged Rule Prompts**: Comes with built-in, reusable rule prompts (as `.mdc` files) for common validation tasks.
*   **History & Deduplication**: Avoids re-running expensive LLM evaluations for unchanged code and criteria.
*   **Comprehensive Reporting**: Get feedback directly in your console and through JUnit XML reports.
*   **Extensible Core Library**: Provides a foundation for CLI, REST, and other potential integrations.

## Project Structure

*   `numerous/pytest_llm_validate/`: The core Python package.
    *   `core.py`: Core logic, including rule loading and evaluation orchestration (planned).
    *   `decorator.py`: Implementation of the `@llm_eval` decorator (planned).
    *   `fixture.py`: Implementation of the `llm_eval()` fixture (planned).
*   `tests/`: Pytest tests for the plugin.
*   `docs/`: Project documentation.
*   `.github/workflows/`: GitHub Actions CI/CD pipeline.

## Getting Started (Conceptual)

While the project is in early development, the intended usage will be simple.

### Using the Decorator

```python
# tests/test_my_module.py
from numerous.pytest_llm_validate.decorator import llm_eval

@llm_eval("The output should be a polite greeting in English.")
def test_greet():
    from my_module import greet
    return greet("World")

# Expected: greet("World") might return "Hello, World!"
# The LLM would then evaluate if "Hello, World!" matches "a polite greeting in English."
```

### Using the Fixture

```python
# tests/test_my_advanced_module.py
# from numerous.pytest_llm_validate.fixture import llm_eval # Path might change

def test_complex_process(llm_eval_fixture): # llm_eval_fixture name may vary
    from my_advanced_module import process_data
    result = process_data({"input": "example"})

    # Obtain a tester instance with a general specification
    # tester = llm_eval_fixture("The process should produce valid outputs.") # API TBD

    # tester.check(result.summary, label="summary should be concise and accurate")
    # tester.check(result.details, label="details should be well-formatted and complete")

# Note: The fixture API is still under design.
```

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines on how to contribute to this project, including branching strategy, commit conventions, and PR procedures.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
