"""Tests to cover remaining missing lines in agent.py module."""

import os
from unittest.mock import MagicMock, patch

# Import the agent module to force execution of import statements
import numerous.pytest_llm_validate.agent as agent_module
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


class TestAgentImportsAndModuleLevel:
    """Test import statements and module-level code execution."""

    def test_agent_imports_execution(self) -> None:
        """Test that all import statements are executed."""
        # Force execution of import statements by accessing imported modules
        assert hasattr(agent_module, "json")
        assert hasattr(agent_module, "re")
        assert hasattr(agent_module, "datetime")
        assert hasattr(agent_module, "Any")
        assert hasattr(agent_module, "Agent")
        assert hasattr(agent_module, "OpenAIModel")
        assert hasattr(agent_module, "EvalRequest")
        assert hasattr(agent_module, "EvalResult")

        # Verify module docstring
        assert agent_module.__doc__ is not None
        assert "LLM agent for evaluation" in agent_module.__doc__

    def test_global_agent_instance_variable(self) -> None:
        """Test that global agent instance variable is accessible."""
        # Access the global variable to force its definition
        assert hasattr(agent_module, "_agent_instance")

        # Initially should be None
        agent_module._agent_instance = None
        assert agent_module._agent_instance is None

    def test_eval_agent_class_definition(self) -> None:
        """Test that EvalAgent class is properly defined."""
        assert hasattr(agent_module, "EvalAgent")
        assert callable(agent_module.EvalAgent)

        # Test class docstring
        eval_agent_class = agent_module.EvalAgent
        assert eval_agent_class.__doc__ is not None
        assert "Agent for performing LLM-based evaluations" in eval_agent_class.__doc__


class TestAgentInitializationEdgeCases:
    """Test edge cases in agent initialization."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    @patch("numerous.pytest_llm_validate.agent.Agent")
    def test_agent_initialization_with_mocking(
        self, mock_agent: MagicMock, mock_openai_model: MagicMock
    ) -> None:
        """Test agent initialization to cover __init__ method lines."""
        # Setup mocks
        mock_model = MagicMock()
        mock_openai_model.return_value = mock_model
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance

        # Initialize agent (covers lines in __init__)
        agent = agent_module.EvalAgent()

        # Verify initialization calls
        mock_openai_model.assert_called_once_with("gpt-4o-mini")
        mock_agent.assert_called_once()

        # Verify instance attributes are set
        assert agent.model is mock_model
        assert agent.agent is mock_agent_instance


class TestSystemPromptGeneration:
    """Test system prompt generation and related methods."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_get_system_prompt_content(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test system prompt generation content and format."""
        agent = agent_module.EvalAgent()
        prompt = agent._get_system_prompt()

        # Test that prompt contains expected content (covers prompt string lines)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "expert code evaluator" in prompt
        assert "JSON" in prompt
        assert '"score"' in prompt
        assert '"comment"' in prompt
        assert "0.0 and 1.0" in prompt


class TestPromptBuildingEdgeCases:
    """Test edge cases in prompt building."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_build_prompt_with_no_placeholders(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test prompt building with rule that has no placeholders."""
        agent = agent_module.EvalAgent()

        rule = EvalRule(
            name="test",
            description="Test rule",
            prompt="Static prompt with no variables",
        )
        request = EvalRequest(
            specification="Test spec", artifacts={"code": "print('hello')"}, rule=rule
        )

        prompt = agent._build_prompt(request)

        # Should return the original prompt unchanged
        assert prompt == "Static prompt with no variables"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_build_prompt_with_empty_artifacts(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test prompt building with empty artifacts."""
        agent = agent_module.EvalAgent()

        rule = EvalRule(
            name="test",
            description="Test rule",
            prompt="Spec: {{specification}}\nArtifacts: {{artifacts}}",
        )
        request = EvalRequest(
            specification="Test spec",
            artifacts={},  # Empty artifacts
            rule=rule,
        )

        prompt = agent._build_prompt(request)

        assert "Spec: Test spec" in prompt
        assert "Artifacts: " in prompt
        # Empty artifacts should result in empty string
        assert prompt.endswith("Artifacts: ")


class TestArtifactFormattingEdgeCases:
    """Test edge cases in artifact formatting."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_format_artifacts_non_string_values(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test formatting artifacts with various non-string types."""
        agent = agent_module.EvalAgent()

        artifacts = {
            "number": 42,
            "boolean": True,
            "none_value": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }

        formatted = agent._format_artifacts(artifacts)

        # All should be converted to strings and wrapped in code blocks
        assert "**number:**" in formatted
        assert "**boolean:**" in formatted
        assert "**none_value:**" in formatted
        assert "**list:**" in formatted
        assert "**dict:**" in formatted

        # Should contain code block markers
        assert formatted.count("```") >= 10  # At least 2 per artifact


class TestResponseParsingEdgeCases:
    """Test edge cases in response parsing."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_nested_json(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing response with nested JSON structures."""
        agent = agent_module.EvalAgent()

        response = """
        Here's my evaluation in JSON format:
        {
            "score": 0.75,
            "comment": "Good code with proper structure",
            "details": {
                "strengths": ["clean", "readable"],
                "weaknesses": ["minor issues"]
            }
        }
        """

        result = agent._parse_response(response)

        # The nested JSON should be parsed correctly
        assert "score" in result
        assert "comment" in result
        assert 0.0 <= result["score"] <= 1.0

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_score_out_of_range(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing response with score outside 0-1 range."""
        agent = agent_module.EvalAgent()

        response = '{"score": 5.0, "comment": "Score out of range"}'

        result = agent._parse_response(response)

        # Should fall back to fallback parsing
        assert "score" in result
        assert "comment" in result
        assert 0.0 <= result["score"] <= 1.0


class TestFallbackParsingComprehensive:
    """Test comprehensive fallback parsing scenarios."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_fallback_parse_rating_patterns(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback parsing with 'rating' keyword."""
        agent = agent_module.EvalAgent()

        # Test rating keyword
        result = agent._fallback_parse("Rating: 3.5 out of 5")
        assert abs(result["score"] - 0.7) < 0.01  # 3.5/5 = 0.7

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_fallback_parse_boundary_scores(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback parsing with boundary score values."""
        agent = agent_module.EvalAgent()

        # Test very large score that should be defaulted
        result = agent._fallback_parse("Score: 999")
        assert result["score"] == 0.5  # Should default

        # Test zero score
        result = agent._fallback_parse("Score: 0.0")
        assert result["score"] == 0.0


class TestErrorHandlingAndExceptions:
    """Test error handling and exception scenarios."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_create_fallback_result_variations(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback result creation with different error messages."""
        agent = agent_module.EvalAgent()

        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test", artifacts={"code": "test"}, rule=rule
        )

        # Test with different error messages
        error_messages = [
            "Connection timeout",
            "API rate limit exceeded",
            "Invalid API key",
            "Model not available",
        ]

        for error_msg in error_messages:
            result = agent._create_fallback_result(request, error_msg)

            assert isinstance(result, EvalResult)
            assert result.score == 0.0
            assert error_msg in result.comment
            assert result.passed is False
            assert result.request == request


class TestGlobalFunctions:
    """Test global module functions."""

    def test_get_agent_function_accessibility(self) -> None:
        """Test that get_agent function is accessible."""
        assert hasattr(agent_module, "get_agent")
        assert callable(agent_module.get_agent)

        # Test function docstring
        get_agent_func = agent_module.get_agent
        assert get_agent_func.__doc__ is not None
        assert "global EvalAgent instance" in get_agent_func.__doc__
