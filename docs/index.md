# pytest-LLM-Validate

A pytest plugin for AI-driven qualitative testing using Large Language Models.

## Overview

pytest-LLM-Validate enables developers to write qualitative tests that are evaluated by Large Language Models (LLMs) rather than traditional assertions. This allows for more flexible and nuanced testing of outputs that are difficult to validate programmatically.

## Features

- **Decorator API**: Use `@llm_eval` to decorate test functions
- **Fixture API**: Use the `llm_eval` fixture for multiple evaluations within a test
- **Rule System**: Configurable evaluation rules for different types of testing
- **Deduplication**: Intelligent caching to avoid redundant LLM calls
- **Multiple LLM Support**: Built on PydanticAI for flexible model integration

## Quick Start

```python
import pytest
from numerous.pytest_llm_validate import llm_eval

@llm_eval("The function should return a polite greeting")
def test_greeting():
    def greet(name):
        return f"Hello, {name}!"
    return greet("World")

def test_multiple_checks(llm_eval):
    tester = llm_eval("Output should be professional and helpful")

    tester.check("Thank you for your inquiry.", label="response1")
    tester.check("I'd be happy to help!", label="response2")

    # Get summary of all evaluations
    summary = tester.get_summary()
    assert summary["passed"] == 2
```

## Installation

```bash
pip install pytest-llm-validate
```

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Documentation

- **[Product Requirements](product-requirements.md)** - Complete product specification with development roadmap
- **[Developer Workflow](developer-workflow.md)** - Comprehensive development guide and best practices
- **[CI Debugging](ci-debugging.md)** - Tools and techniques for debugging CI pipeline issues
- **[Technical Resume](resume.md)** - Detailed technical architecture and implementation details
