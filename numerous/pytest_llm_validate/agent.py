"""LLM agent for evaluation using PydanticAI."""

import json
import re
from datetime import datetime
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from .models import EvalRequest, EvalResult


class EvalAgent:
    """Agent for performing LLM-based evaluations."""

    def __init__(self) -> None:
        """Initialize the evaluation agent."""
        # Use OpenAI model (gpt-4o-mini as specified in PRD)
        self.model = OpenAIModel("gpt-4o-mini")

        # Create PydanticAI agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for evaluation."""
        return """You are an expert code evaluator. Your task is to evaluate code outputs against given specifications and return structured feedback.

You must respond with valid JSON in exactly this format:
{
    "score": 0.85,
    "comment": "Detailed explanation of your evaluation"
}

The score must be a number between 0.0 and 1.0.
The comment should explain your reasoning clearly and constructively."""

    async def evaluate(self, request: EvalRequest) -> EvalResult:
        """Evaluate a request using the LLM agent."""
        try:
            # Build the prompt using the rule template
            prompt = self._build_prompt(request)

            # Run the agent
            response = await self.agent.run(prompt)

            # Parse the response
            eval_data = self._parse_response(response.data)

            # Create result
            result = EvalResult(
                score=eval_data["score"],
                comment=eval_data["comment"],
                passed=eval_data["score"] >= request.threshold,
                request=request,
                model_used=request.model,
                timestamp=datetime.now().isoformat(),
            )

            return result

        except Exception as e:
            # Fallback evaluation in case of errors
            return self._create_fallback_result(request, str(e))

    def _build_prompt(self, request: EvalRequest) -> str:
        """Build the evaluation prompt from the request."""
        # Replace template variables in the rule prompt
        prompt = request.rule.prompt

        # Replace {{specification}} and {{artifacts}} placeholders
        prompt = prompt.replace("{{specification}}", request.specification)
        prompt = prompt.replace(
            "{{artifacts}}", self._format_artifacts(request.artifacts)
        )

        return prompt

    def _format_artifacts(self, artifacts: dict[str, Any]) -> str:
        """Format artifacts for the prompt."""
        formatted_lines = []

        for key, value in artifacts.items():
            if isinstance(value, str):
                formatted_lines.append(f"**{key}:**\n```\n{value}\n```")
            else:
                formatted_lines.append(f"**{key}:**\n```\n{str(value)}\n```")

        return "\n\n".join(formatted_lines)

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse the LLM response into structured data."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # Validate required fields
                if "score" in data and "comment" in data:
                    # Ensure score is valid
                    score = float(data["score"])
                    if 0.0 <= score <= 1.0:
                        return {"score": score, "comment": str(data["comment"])}

            # Fallback parsing if JSON extraction fails
            return self._fallback_parse(response_text)

        except (json.JSONDecodeError, ValueError, KeyError):
            return self._fallback_parse(response_text)

    def _fallback_parse(self, response_text: str) -> dict[str, Any]:
        """Fallback parsing when JSON parsing fails."""
        # Try to extract a numerical score from the text
        score_match = re.search(
            r"(?:score|rating)[:\s]*([0-9]*\.?[0-9]+)", response_text, re.IGNORECASE
        )

        if score_match:
            try:
                score = float(score_match.group(1))
                # Normalize score if it's out of 0-1 range
                if score > 1.0:
                    if score <= 5.0:
                        score = score / 5.0  # Assume 5-point scale
                    elif score <= 10.0:
                        score = score / 10.0  # Assume 10-point scale
                    elif score <= 100.0:
                        score = score / 100.0  # Assume percentage
                    else:
                        score = 0.5  # Default if unclear

                return {
                    "score": max(0.0, min(1.0, score)),
                    "comment": f"Evaluation completed. Response: {response_text[:200]}...",
                }
            except ValueError:
                pass

        # Ultimate fallback
        return {
            "score": 0.5,
            "comment": f"Could not parse evaluation response. Raw response: {response_text[:200]}...",
        }

    def _create_fallback_result(
        self, request: EvalRequest, error_msg: str
    ) -> EvalResult:
        """Create a fallback result when evaluation fails."""
        return EvalResult(
            score=0.0,
            comment=f"Evaluation failed: {error_msg}",
            passed=False,
            request=request,
            model_used=request.model,
            timestamp=datetime.now().isoformat(),
        )


# Global agent instance
_agent_instance: EvalAgent | None = None


def get_agent() -> EvalAgent:
    """Get the global EvalAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EvalAgent()
    return _agent_instance
