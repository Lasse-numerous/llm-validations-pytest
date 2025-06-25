# LLM Inspection Guide

This document explains how to inspect LLM evaluation results when using pytest-llm-validate.

## Inspecting LLM Evaluation Results

### Using Logging (Recommended)

The plugin includes comprehensive logging to help you inspect LLM evaluation results:

#### Basic Logging
```bash
# Run with verbose output to see LLM evaluation results
pytest examples/basic_usage_example.py -v -s

# Run with debug output for detailed information
pytest examples/basic_usage_example.py -vv -s
```

#### Custom Log Level
```bash
# Set custom log level via environment variable
PYTEST_LLM_VALIDATE_LOG_LEVEL=DEBUG pytest examples/basic_usage_example.py -s
```

#### What You'll See
The logging output includes:
- **Evaluation Score**: Numerical score (0.0-1.0) from the LLM
- **Pass/Fail Status**: Whether the evaluation passed the threshold  
- **LLM Feedback**: Detailed explanation from the LLM about the evaluation
- **Artifacts**: (Debug level) The actual content that was evaluated

Example log output:
```
[LLM-VALIDATE] INFO: LLM Evaluation Result for complaint_handling: Score=0.85, Passed=True, Threshold=0.70
[LLM-VALIDATE] INFO: LLM Feedback for complaint_handling: The email response demonstrates excellent professionalism and empathy...
```

### Using the Fixture API

You can also programmatically access results:

```python
def test_multiple_outputs(llm_eval):
    tester = llm_eval("All outputs should be professional")
    
    # Perform checks
    tester.check(output1, label="first_check")
    tester.check(output2, label="second_check")
    
    # Get detailed results
    results = tester.get_results()
    for result in results:
        print(f"Score: {result.score}, Comment: {result.comment}")
    
    # Get summary
    summary = tester.get_summary()
    print(f"Average score: {summary['average_score']}")
    
    # Log summary to pytest logs
    tester.log_summary()
```

## Recommended Testing Approach

### Hybrid Approach (Best Practice)

Combine traditional assertions with LLM evaluation:

```python
def test_greeting(llm_eval):
    def greet(name):
        return f"Hello, {name}!"
    
    result = greet("World")
    
    # Traditional assertions (fast, reliable)
    assert "World" in result
    assert result.startswith("Hello")
    
    # LLM evaluation (qualitative assessment)
    tester = llm_eval("The greeting should be warm and friendly")
    tester.check(result, label="greeting_quality")
```

This approach gives you:
- **Fast feedback** from traditional assertions
- **Qualitative assessment** from LLM evaluation
- **Clear separation** between structural and qualitative testing

### Multiple Evaluations in One Test

```python
def test_email_responses(llm_eval):
    tester = llm_eval("Emails should be professional and helpful")
    
    complaint_email = generate_email("complaint")
    tester.check(complaint_email, label="complaint_handling")
    
    inquiry_email = generate_email("inquiry") 
    tester.check(inquiry_email, label="inquiry_response")
    
    # Summary will show results for each labeled check
    tester.log_summary()
```

## Configuration Options

### Environment Variables

- `PYTEST_LLM_VALIDATE_LOG_LEVEL`: Set to `DEBUG`, `INFO`, `WARNING`, or `ERROR`
- `OPENAI_API_KEY`: Required for LLM evaluations

### Pytest Flags

- `-v`: Verbose output (shows INFO level logs)
- `-vv`: Very verbose output (shows DEBUG level logs)  
- `-s`: Don't capture stdout (required to see logs in real-time)

### Fixture Parameters

```python
def test_example(llm_eval):
    # Configure the tester
    tester = llm_eval(
        "Specification for evaluation",
        threshold=0.8,              # Score threshold (0.0-1.0)
        model="gpt-4o-mini",       # LLM model to use
        rule="output_format",       # Evaluation rule
        no_dedupe=False,           # Enable result caching (default: True for fresh evaluations)
        project="my_project",       # Custom metadata
        version="1.0"
    )
    
    tester.check(output, label="descriptive_label")
```

## Troubleshooting

### Issue: Not seeing log output
**Solution**: Make sure to use the `-s` flag: `pytest -v -s`

### Issue: Too much log output
**Solution**: Set log level to WARNING: `PYTEST_LLM_VALIDATE_LOG_LEVEL=WARNING pytest -v -s`

### Issue: API key errors
**Solution**: Set your OpenAI API key: `export OPENAI_API_KEY=your_key_here`

### Issue: Tests are slow
**Solution**: Set `no_dedupe=False` to enable caching results, and combine multiple traditional assertions before LLM evaluation

## Best Practices

1. **Use descriptive labels** for better log readability
2. **Combine traditional and LLM testing** for comprehensive coverage
3. **Use appropriate thresholds** - higher for critical functionality
4. **Enable logging during development** to understand LLM reasoning
5. **Group related checks** in single tests with multiple `.check()` calls 