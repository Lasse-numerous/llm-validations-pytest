# Architecture

Technical architecture and design decisions for pytest-LLM-Validate, covering system components, data flow, and implementation details.

## System Overview

pytest-LLM-Validate is built as a pytest plugin that integrates Large Language Model evaluation into the test execution pipeline. The architecture emphasizes modularity, performance, and reliability.

```mermaid
graph TB
    subgraph "Test Execution"
        T[Test Function] --> D[@llm_eval Decorator]
        T --> F[llm_eval Fixture]
        D --> C[Capture Outputs]
        F --> TI[Tester Instance]
    end

    subgraph "Core Components"
        C --> ER[EvalRequest]
        TI --> ER
        ER --> A[Agent]
        A --> LLM[OpenAI API]
        A --> R[EvalResult]
    end

    subgraph "Supporting Systems"
        ER --> H[History Cache]
        ER --> L[Rule Loader]
        L --> RU[Built-in Rules]
        L --> CR[Custom Rules]
        H --> FS[File System Cache]
    end

    subgraph "Output"
        R --> AS[Assertion/Summary]
        R --> RE[Test Report]
        H --> R
    end
```

## Core Components

### 1. Plugin System

#### Plugin Registration

*Source: [`numerous/pytest_llm_validate/plugin.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/plugin.py)*

The plugin registers with pytest via entry points and provides the core `llm_eval` fixture:

```python
@pytest.fixture
def llm_eval() -> Callable[..., Any]:
    """Pytest fixture for LLM-based evaluation."""
    return create_llm_eval_tester
```

**Design Decisions:**
- Single fixture approach for simplicity
- Factory pattern for creating tester instances
- Automatic plugin discovery via entry points

### 2. Decorator API

#### Implementation

*Source: [`numerous/pytest_llm_validate/decorator.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/decorator.py)*

The decorator wraps test functions to capture outputs and perform evaluation:

```python
def llm_eval(specification: str, **options) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Capture stdout/stderr
            # 2. Execute test function
            # 3. Handle exceptions
            # 4. Create EvalRequest
            # 5. Perform evaluation
            # 6. Assert on result
            return result
        return wrapper
    return decorator
```

**Key Features:**
- Output capture using `io.StringIO`
- Exception handling and formatting
- Async LLM evaluation in sync context
- Detailed assertion errors

### 3. Fixture API

#### LLMTester Class

*Source: [`numerous/pytest_llm_validate/fixture.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/fixture.py)*

The fixture API provides a `LLMTester` class for multiple evaluations:

```python
class LLMTester:
    def __init__(self, specification: str, **options):
        self.specification = specification
        self.results: list[EvalResult] = []
        # Configure evaluation parameters

    def check(self, output: Any, **metadata) -> None:
        # Create evaluation request
        # Perform evaluation (with caching)
        # Store result
        # Assert on failure

    def get_results(self) -> list[EvalResult]:
        return self.results.copy()

    def get_summary(self) -> dict[str, Any]:
        # Calculate summary statistics
```

**Design Patterns:**
- Builder pattern for configuration
- Command pattern for checks
- Observer pattern for result collection

### 4. Data Models

#### Core Models

*Source: [`numerous/pytest_llm_validate/models.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/models.py)*

Pydantic models ensure type safety and validation:

```python
class EvalRule(BaseModel):
    """Rule containing prompts and configuration."""
    name: str
    description: str
    prompt: str
    version: str = "1.0"
    author: str = "pytest-llm-validate"
    tags: list[str] = Field(default_factory=list)

class EvalRequest(BaseModel):
    """Request structure for LLM evaluation."""
    specification: str
    artifacts: dict[str, Any]
    rule: EvalRule
    threshold: float = 0.7
    model: str = "gpt-4o-mini"
    metadata: dict[str, Any] = Field(default_factory=dict)

class EvalResult(BaseModel):
    """Result structure from LLM evaluation."""
    score: float
    comment: str
    passed: bool
    request: EvalRequest
    model_used: str
    timestamp: str
```

**Design Benefits:**
- Type safety with Pydantic validation
- JSON serialization for caching
- Clear data contracts between components
- Extensible metadata system

## Agent System

### LLM Integration

*Source: [`numerous/pytest_llm_validate/agent.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/agent.py)*

The agent system handles LLM communication using PydanticAI:

```python
class EvalAgent:
    def __init__(self):
        self.agent = Agent(
            "openai:gpt-4o-mini",
            result_type=dict,
            system_prompt=self.SYSTEM_PROMPT
        )

    async def evaluate(self, request: EvalRequest) -> EvalResult:
        # Build prompt from rule template
        # Execute LLM request
        # Parse response
        # Handle errors
        # Return structured result
```

**Architecture Features:**
- Async-first design for performance
- Structured output parsing
- Error handling and fallbacks
- Configurable models and parameters

### Prompt Engineering

The system uses a template-based approach for prompt construction:

```python
def _build_prompt(self, request: EvalRequest) -> str:
    prompt = request.rule.prompt
    prompt = prompt.replace("{{specification}}", request.specification)
    prompt = prompt.replace("{{artifacts}}", self._format_artifacts(request.artifacts))
    return prompt
```

**Template Variables:**
- `{{specification}}` - User's natural language spec
- `{{artifacts}}` - Formatted test outputs
- Rule-specific variables can be added

## Caching and Deduplication

### History System

*Source: [`numerous/pytest_llm_validate/history.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/history.py)*

The history system provides intelligent caching to avoid redundant LLM calls:

```python
class EvalHistory:
    def __init__(self):
        self.cache: dict[str, EvalResult] = {}
        self.file_path = ".pytest-llm-validate-history.json"

    def get_cached_result(self, request: EvalRequest) -> EvalResult | None:
        key = self._generate_cache_key(request)
        return self.cache.get(key)

    def cache_result(self, result: EvalResult) -> None:
        key = self._generate_cache_key(result.request)
        self.cache[key] = result
        self._persist_cache()
```

**Caching Strategy:**
- Content-based hashing for cache keys
- JSON persistence between test runs
- LRU eviction for memory management
- Configurable TTL and size limits

### Cache Key Generation

Cache keys are generated from request content to ensure identical evaluations reuse results:

```python
def _generate_cache_key(self, request: EvalRequest) -> str:
    # Combine specification, artifacts, rule, and key metadata
    cache_content = {
        "specification": request.specification,
        "artifacts": request.artifacts,
        "rule": request.rule.name,
        "model": request.model,
        "threshold": request.threshold
    }
    content_str = json.dumps(cache_content, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()
```

## Rule System

### Rule Loading

*Source: [`numerous/pytest_llm_validate/loader.py`](https://github.com/numerous-com/pytest-llm-validate/blob/main/numerous/pytest_llm_validate/loader.py)*

The rule system loads evaluation rules from Markdown-Cursor (.mdc) files:

```python
def get_rule(name: str) -> EvalRule | None:
    # Search built-in rules
    # Search custom rule directories
    # Parse .mdc file format
    # Return EvalRule instance

def parse_mdc_file(file_path: Path) -> EvalRule:
    # Parse markdown metadata
    # Extract prompt content
    # Create EvalRule instance
```

**Rule Format (.mdc files):**
```markdown
**Author:** team-name
**Tags:** quality, security, performance

## Evaluation Prompt

Your evaluation prompt content here with {{specification}} and {{artifacts}} placeholders.

### Response Format
```json
{
  "score": 0.85,
  "comment": "Detailed feedback..."
}
```
```

### Built-in Rules

The system includes three built-in evaluation rules:

1. **`general_quality`** - Overall code/content quality assessment
2. **`output_format`** - Structure and formatting evaluation
3. **`test_behavior`** - Test-specific behavior validation

Each rule is specialized for different evaluation contexts and includes specific criteria and scoring guidelines.

## Error Handling

### Graceful Degradation

The system implements multiple layers of error handling:

```python
async def evaluate(self, request: EvalRequest) -> EvalResult:
    try:
        # Primary evaluation path
        response = await self.agent.run(prompt)
        return self._parse_response(response.data)
    except Exception as e:
        # Fallback evaluation with error details
        return self._create_fallback_result(request, str(e))
```

**Error Handling Strategies:**
- Fallback evaluations on API failures
- Graceful parsing of malformed responses
- Detailed error logging and reporting
- Configurable retry logic

### Response Parsing

The system includes robust response parsing with fallbacks:

```python
def _parse_response(self, response_text: str) -> dict[str, Any]:
    try:
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response_text)
        if json_match:
            data = json.loads(json_match.group(0))
            return {"score": float(data["score"]), "comment": str(data["comment"])}
        # Fallback parsing
        return self._fallback_parse(response_text)
    except (json.JSONDecodeError, ValueError):
        return self._fallback_parse(response_text)
```

## Performance Considerations

### Asynchronous Processing

All LLM interactions are asynchronous to prevent blocking test execution:

```python
# Sync wrapper for async evaluation
try:
    eval_result = asyncio.run(get_agent().evaluate(request))
except RuntimeError:
    # Handle existing event loop
    loop = asyncio.get_event_loop()
    eval_result = loop.run_until_complete(get_agent().evaluate(request))
```

### Memory Management

- Lazy loading of rules and agents
- LRU cache eviction for history
- Efficient JSON serialization
- Minimal memory footprint per test

### Cost Optimization

- Intelligent deduplication
- Configurable model selection
- Batch processing capabilities
- Usage tracking and warnings

## Extensibility

### Custom Rules

The architecture supports custom rules through:

- Plugin-style rule directory registration
- Standardized .mdc file format
- Template variable system
- Rule versioning and metadata

### Custom Models

Model configuration is externalized for easy extension:

```python
# Environment-based model selection
model = os.getenv("PYTEST_LLM_VALIDATE_MODEL", "gpt-4o-mini")

# Per-test model override
@llm_eval("Specification", model="gpt-4o")
def test_critical_functionality():
    pass
```

### Plugin Hooks

The system provides hooks for extending functionality:

- Custom error handlers
- Result post-processing
- Cache strategies
- Authentication methods

## Security Considerations

### Data Privacy

- No persistent storage of sensitive test data
- Configurable cache encryption
- API key management best practices
- Optional data sanitization

### API Security

- Secure credential handling
- Request timeout configuration
- Rate limiting awareness
- Error message sanitization

## Testing Strategy

The plugin itself uses a comprehensive testing approach:

### Unit Testing

- Isolated component testing
- Mock-based LLM interactions
- Edge case coverage
- Performance benchmarking

### Integration Testing

- End-to-end test scenarios
- Real LLM API integration
- CI/CD pipeline validation
- Cross-platform compatibility

### Self-Testing

The plugin uses itself for qualitative testing:

```python
@llm_eval("Error messages should be helpful and actionable")
def test_error_message_quality():
    try:
        invalid_operation()
    except Exception as e:
        return format_error_message(e)
```

This architecture provides a robust, extensible foundation for AI-driven qualitative testing while maintaining simplicity and performance.
