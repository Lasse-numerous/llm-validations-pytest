"""Core data models for pytest-llm-validate."""

from typing import Any

from pydantic import BaseModel, Field


class EvalRule(BaseModel):
    """A rule containing prompts and configuration for LLM evaluation."""

    name: str = Field(description="Unique identifier for the rule")
    description: str = Field(
        description="Human-readable description of what this rule evaluates"
    )
    prompt: str = Field(description="The actual LLM prompt template")
    version: str = Field(default="1.0", description="Version of the rule")
    author: str = Field(default="pytest-llm-validate", description="Author of the rule")
    tags: list[str] = Field(
        default_factory=list, description="Tags for categorizing rules"
    )


class EvalRequest(BaseModel):
    """Request structure for LLM evaluation."""

    specification: str = Field(description="Natural language specification from user")
    artifacts: dict[str, Any] = Field(description="Code outputs to evaluate")
    rule: EvalRule = Field(description="Rule to use for evaluation")
    threshold: float = Field(
        default=0.7, description="Minimum score threshold for passing"
    )
    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class EvalResult(BaseModel):
    """Result structure from LLM evaluation."""

    score: float = Field(description="Numerical score between 0.0 and 1.0")
    comment: str = Field(description="Detailed explanation from the LLM")
    passed: bool = Field(description="Whether the evaluation passed the threshold")
    request: EvalRequest = Field(
        description="Original request that generated this result"
    )
    model_used: str = Field(description="Actual model used for evaluation")
    timestamp: str = Field(description="ISO timestamp of evaluation")

    @property
    def passed_threshold(self) -> bool:
        """Check if score meets the threshold requirement."""
        return self.score >= self.request.threshold
