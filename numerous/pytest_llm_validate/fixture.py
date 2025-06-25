"""Fixture API implementation for llm_eval pytest fixture."""

import asyncio
import logging
from typing import Any

from .agent import get_agent
from .history import get_history
from .loader import get_default_rule, get_rule
from .models import EvalRequest, EvalResult

# Configure logger for LLM evaluation results
logger = logging.getLogger("pytest_llm_validate")


class LLMTester:
    """Tester object for performing multiple LLM evaluations."""

    def __init__(
        self,
        specification: str,
        *,
        threshold: float = 0.7,
        model: str = "gpt-4o-mini",
        rule: str | None = None,
        no_dedupe: bool = True,
        **metadata: Any,
    ) -> None:
        """Initialize the tester.

        Args:
            specification: Natural language specification for evaluation
            threshold: Minimum score threshold for passing (0.0 to 1.0)
            model: LLM model to use for evaluation
            rule: Name of evaluation rule to use (defaults to 'general_quality')
            no_dedupe: If True, skip deduplication and always perform fresh evaluation (default: True)
            **metadata: Additional metadata to include in evaluations
        """
        self.specification = specification
        self.threshold = threshold
        self.model = model
        self.rule_name = rule
        self.no_dedupe = no_dedupe
        self.metadata = metadata

        # Get the evaluation rule
        if rule is not None:
            self.eval_rule = get_rule(rule) or get_default_rule()
        else:
            self.eval_rule = get_default_rule()

        # Storage for multiple checks
        self.checks: list[dict[str, Any]] = []
        self.results: list[EvalResult] = []

    def check(
        self, output: Any, *, label: str | None = None, **check_metadata: Any
    ) -> None:
        """Perform a check on the given output.

        Args:
            output: The output to evaluate
            label: Optional label for this specific check
            **check_metadata: Additional metadata for this specific check

        Raises:
            AssertionError: If the evaluation fails to meet the threshold
        """
        # Create artifacts for this specific check
        artifacts: dict[str, Any] = {
            "output": output,
        }

        # Add label if provided
        if label:
            artifacts["label"] = label

        # Combine global and check-specific metadata
        combined_metadata = {**self.metadata, **check_metadata}
        if combined_metadata:
            artifacts["metadata"] = combined_metadata

        # Store check information
        check_info = {
            "output": output,
            "label": label,
            "metadata": check_metadata,
            "artifacts": artifacts,
        }
        self.checks.append(check_info)

        # Create evaluation request
        request = EvalRequest(
            specification=self.specification,
            artifacts=artifacts,
            rule=self.eval_rule,
            threshold=self.threshold,
            model=self.model,
            metadata=combined_metadata,
        )

        # Perform evaluation (with deduplication if enabled)
        if self.no_dedupe:
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
            if not self.no_dedupe:
                get_history().cache_result(eval_result)

        # Store result
        self.results.append(eval_result)

        # Log the evaluation result for inspection
        check_identifier = f"{label}" if label else f"check_{len(self.results)}"
        logger.info(
            f"LLM Evaluation Result for {check_identifier}: "
            f"Score={eval_result.score:.2f}, "
            f"Passed={eval_result.passed}, "
            f"Threshold={self.threshold:.2f}"
        )
        logger.info(f"LLM Feedback for {check_identifier}: {eval_result.comment}")
        
        # For detailed logging, also log the artifacts
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Artifacts for {check_identifier}: {artifacts}")

        # Assert based on evaluation result
        if not eval_result.passed:
            check_label = f" ({label})" if label else ""
            raise AssertionError(
                f"LLM Evaluation Failed{check_label} (score: {eval_result.score:.2f}, "
                f"threshold: {self.threshold:.2f})\n"
                f"Specification: {self.specification}\n"
                f"Output: {output}\n"
                f"LLM Feedback: {eval_result.comment}"
            )

    def get_results(self) -> list[EvalResult]:
        """Get all evaluation results from checks performed so far."""
        return self.results.copy()

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all checks and their results."""
        if not self.results:
            return {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "average_score": 0.0,
                "checks": [],
            }

        passed = sum(1 for result in self.results if result.passed)
        failed = len(self.results) - passed
        avg_score = sum(result.score for result in self.results) / len(self.results)

        check_summaries = []
        for i, (check, result) in enumerate(
            zip(self.checks, self.results, strict=False)
        ):
            check_summaries.append(
                {
                    "index": i,
                    "label": check.get("label"),
                    "score": result.score,
                    "passed": result.passed,
                    "comment": result.comment,
                }
            )

        return {
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "average_score": avg_score,
            "checks": check_summaries,
        }

    def log_summary(self) -> None:
        """Log a summary of all evaluation results."""
        summary = self.get_summary()
        logger.info(
            f"LLM Evaluation Summary: "
            f"{summary['total_checks']} checks, "
            f"{summary['passed']} passed, "
            f"{summary['failed']} failed, "
            f"average score: {summary['average_score']:.2f}"
        )
        
        for check_summary in summary['checks']:
            logger.info(
                f"  Check {check_summary['index']} "
                f"({check_summary['label'] or 'unlabeled'}): "
                f"Score={check_summary['score']:.2f}, "
                f"Passed={check_summary['passed']}"
            )


def create_llm_eval_tester(
    specification: str,
    *,
    threshold: float = 0.7,
    model: str = "gpt-4o-mini",
    rule: str | None = None,
    no_dedupe: bool = True,
    **metadata: Any,
) -> LLMTester:
    """Create a new Tester instance for LLM evaluation.

    This function is used by the pytest fixture to create Tester objects.

    Args:
        specification: Natural language specification for evaluation
        threshold: Minimum score threshold for passing (0.0 to 1.0)
        model: LLM model to use for evaluation
        rule: Name of evaluation rule to use (defaults to 'general_quality')
        no_dedupe: If True, skip deduplication and always perform fresh evaluation (default: True)
        **metadata: Additional metadata to include in evaluations

    Returns:
        Tester instance ready for performing checks

    Example:
        def test_multiple_outputs(llm_eval):
            tester = llm_eval("All outputs should be professional")
            tester.check("Hello, how are you?", label="greeting")
            tester.check("Thank you for your inquiry.", label="response")
    """
    return LLMTester(
        specification,
        threshold=threshold,
        model=model,
        rule=rule,
        no_dedupe=no_dedupe,
        **metadata,
    )
