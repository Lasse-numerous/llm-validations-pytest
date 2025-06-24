"""Decorator implementation for @llm_eval."""

import asyncio
import functools
import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Dict, Optional

from .agent import get_agent
from .loader import get_default_rule
from .models import EvalRequest
from .history import get_history


def llm_eval(
    specification: str,
    *,
    threshold: float = 0.7,
    model: str = "gpt-4o-mini",
    rule: Optional[str] = None,
    no_dedupe: bool = False,
    **metadata: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for LLM-based evaluation of test outputs.
    
    Args:
        specification: Natural language specification describing expected behavior
        threshold: Minimum score threshold for passing (0.0 to 1.0)
        model: LLM model to use for evaluation
        rule: Name of evaluation rule to use (defaults to 'general_quality')
        no_dedupe: If True, skip deduplication and always perform fresh evaluation
        **metadata: Additional metadata to include in the evaluation
        
    Returns:
        Decorated test function that performs LLM evaluation
        
    Example:
        @llm_eval("The function should return a polite greeting")
        def test_greeting():
            def greet(name):
                return f"Hello, {name}!"
            return greet("World")
    """
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Capture stdout and stderr
            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()
            
            # Execute the test function with output capture
            with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    # If the test function itself raises an exception, 
                    # include that in the artifacts for evaluation
                    result = f"Exception: {type(e).__name__}: {e}"
            
            # Collect captured outputs
            stdout_content = captured_stdout.getvalue()
            stderr_content = captured_stderr.getvalue()
            
            # Build artifacts dictionary
            artifacts: Dict[str, Any] = {
                "return_value": result,
            }
            
            # Only include stdout/stderr if they have content
            if stdout_content.strip():
                artifacts["stdout"] = stdout_content
            if stderr_content.strip():
                artifacts["stderr"] = stderr_content
            
            # Add any additional metadata
            if metadata:
                artifacts["metadata"] = metadata
            
            # Get the evaluation rule
            from .loader import get_rule
            eval_rule = get_rule(rule) if rule else get_default_rule()
            
            # Create evaluation request
            request = EvalRequest(
                specification=specification,
                artifacts=artifacts,
                rule=eval_rule,
                threshold=threshold,
                model=model,
                metadata=metadata
            )
            
            # Perform evaluation (with deduplication if enabled)
            if no_dedupe:
                # Skip deduplication, always evaluate fresh
                eval_result = None
            else:
                # Check for cached result
                eval_result = get_history().get_cached_result(request)
            
            if eval_result is None:
                # No cached result, perform fresh evaluation
                try:
                    # Run async evaluation in sync context
                    eval_result = asyncio.get_event_loop().run_until_complete(
                        get_agent().evaluate(request)
                    )
                except RuntimeError:
                    # If no event loop is running, create a new one
                    eval_result = asyncio.run(get_agent().evaluate(request))
                
                # Cache the result if deduplication is enabled
                if not no_dedupe:
                    get_history().cache_result(eval_result)
            
            # Assert based on evaluation result
            if not eval_result.passed:
                raise AssertionError(
                    f"LLM Evaluation Failed (score: {eval_result.score:.2f}, "
                    f"threshold: {threshold:.2f})\n"
                    f"Specification: {specification}\n"
                    f"LLM Feedback: {eval_result.comment}"
                )
            
            # Return the original result for further test processing if needed
            return result
        
        return wrapper
    return decorator