from pydantic import BaseModel, Field

class EvalRule(BaseModel):
    """
    Represents an evaluation rule loaded from an .mdc file.
    """
    id: str = Field(..., description="Unique identifier for the rule, often derived from the filename or frontmatter.")
    name: str = Field(..., description="Human-readable name for the rule.")
    description: str = Field(..., description="Detailed description of what the rule does and when it should be used.")
    prompt_template: str = Field(..., description="The template string for the prompt, which may include placeholders like {captured_output} and {user_specification}.")

    # Future considerations:
    # - expected_schema: Optional[Type[BaseModel]] = Field(None, description="Pydantic model defining the expected structure of the LLM's response for this rule.")
    # - default_model_parameters: Optional[dict] = Field(None, description="Default parameters for the LLM when using this rule, e.g., temperature.")

# Example of another model that will be used later, defined here for co-location of core data structures.
class EvalResult(BaseModel):
    """
    Represents the result of an LLM evaluation for a single check.
    This model will be populated by the PydanticAI agent.
    """
    passed: bool = Field(..., description="Whether the evaluation passed or failed based on the criteria.")
    comment: str = Field(..., description="The LLM's reasoning or comment explaining the evaluation outcome.")
    score: Optional[float] = Field(None, description="An optional numeric score (e.g., 0.0-1.0) if the rule/LLM provides one.")
    # rule_id_used: Optional[str] = Field(None, description="The ID of the EvalRule that was used for this evaluation.")
    # error_message: Optional[str] = Field(None, description="Any error message if the evaluation itself failed.")

# Placeholder for request structure, will be fleshed out in Task 2.2
# class EvalRequest(BaseModel):
#     """
#     Represents a request to the LLM for evaluation.
#     """
#     user_specification: str
#     captured_output: Any # Could be str, dict, etc.
#     rule_id: str
#     # ... other relevant context
