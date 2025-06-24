# pytest-LLM-Validate

A pytest plugin and toolkit that lets developers embed **AI-driven qualitative & behavioural tests** into their codebase with minimal boilerplate.

## Overview

`pytest-LLM-Validate` enables you to write tests that validate code outputs against natural-language specifications using Large Language Models. The plugin provides two convenient APIs:

1. **Decorator API** – annotate a test with `@llm_eval`, return the artefact to evaluate
2. **Object/Fixture API** – obtain a tester object via `llm_eval("spec", **opts)`, then call `tester.check(output, label="...")` for flexible multiple checks

## Quick Start

### Installation

```bash
pip install pytest-llm-validate
```

### Basic Usage

#### Decorator API

```python
import pytest
from numerous.pytest_llm_validate import llm_eval

@llm_eval("The function should return a polite greeting")
def test_greeting():
    def greet(name):
        return f"Hello, {name}!"

    return greet("World")
```

#### Fixture API

```python
def test_multiple_outputs(llm_eval):
    tester = llm_eval("All outputs should be professional and helpful")

    result1 = generate_email_response("complaint")
    tester.check(result1, label="complaint_response")

    result2 = generate_email_response("inquiry")
    tester.check(result2, label="inquiry_response")
```

## Features

- **Built-in rule prompts** packaged as Markdown-Cursor (`.mdc`) files
- **PydanticAI integration** for reliable LLM interactions
- **Deduplication** to skip repeated evaluations
- **Rich reporting** with console tables and JUnit XML output
- **CLI interface** for standalone usage
- **FastAPI REST API** for integration scenarios
- **MCP (Model Context Protocol)** support for AI assistants

## Requirements

- Python ≥ 3.12, < 3.14
- OpenAI API key (tested with o4-mini)

## Development

```bash
git clone https://github.com/numerous-com/pytest-llm-validate
cd pytest-llm-validate
pip install -e ".[dev]"
pre-commit install
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and contribution process.
# Test change
