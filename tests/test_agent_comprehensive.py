"""Comprehensive tests for numerous.pytest_llm_validate.agent module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


class TestEvalAgentWithMocking:
    """Test cases for EvalAgent class with proper mocking."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_eval_agent_initialization(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test EvalAgent initialization with mocked dependencies."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        mock_model = MagicMock()
        mock_openai_model.return_value = mock_model
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance

        agent = EvalAgent()

        # Verify initialization
        assert agent.model is mock_model
        assert agent.agent is mock_agent_instance
        mock_openai_model.assert_called_once_with("gpt-4o-mini")
        mock_agent.assert_called_once()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_get_system_prompt(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test system prompt generation."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        prompt = agent._get_system_prompt()

        assert isinstance(prompt, str)
        assert "JSON" in prompt
        assert "score" in prompt
        assert "comment" in prompt
        assert "0.0 and 1.0" in prompt

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_build_prompt(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test prompt building with template substitution."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        rule = EvalRule(
            name="test",
            description="Test rule",
            prompt="Specification: {{specification}}\nArtifacts: {{artifacts}}",
        )
        request = EvalRequest(
            specification="Code should be clean",
            artifacts={"code": "print('hello')", "output": "hello"},
            rule=rule,
        )

        prompt = agent._build_prompt(request)

        assert "Specification: Code should be clean" in prompt
        assert "Artifacts:" in prompt
        assert "print('hello')" in prompt
        assert "hello" in prompt

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_format_artifacts_string(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test formatting string artifacts."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        artifacts = {"code": "def hello(): pass"}

        formatted = agent._format_artifacts(artifacts)

        assert "**code:**" in formatted
        assert "def hello(): pass" in formatted
        assert "```" in formatted

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_format_artifacts_mixed_types(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test formatting mixed type artifacts."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        artifacts = {
            "code": "print('hello')",
            "number": 42,
            "list": ["a", "b", "c"],
            "dict": {"key": "value"},
        }

        formatted = agent._format_artifacts(artifacts)

        assert "**code:**" in formatted
        assert "**number:**" in formatted
        assert "**list:**" in formatted
        assert "**dict:**" in formatted
        assert "print('hello')" in formatted
        assert "42" in formatted
        assert "['a', 'b', 'c']" in formatted
        assert "{'key': 'value'}" in formatted

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_valid_json(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing valid JSON response."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        response = '{"score": 0.85, "comment": "Good code quality"}'

        result = agent._parse_response(response)

        assert result["score"] == 0.85
        assert result["comment"] == "Good code quality"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_json_in_text(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing JSON embedded in text."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        response = 'Here is my evaluation: {"score": 0.9, "comment": "Excellent work"} That concludes the review.'

        result = agent._parse_response(response)

        assert result["score"] == 0.9
        assert result["comment"] == "Excellent work"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_invalid_json_fallback(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback parsing for invalid JSON."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        response = "The code quality score is 8.5 out of 10. It looks good overall."

        result = agent._parse_response(response)

        assert "score" in result
        assert "comment" in result
        assert 0.0 <= result["score"] <= 1.0
        assert isinstance(result["comment"], str)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_fallback_parse_score_patterns(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback parsing with various score patterns."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()

        # Test 5-point scale
        result = agent._fallback_parse("Rating: 4.2 out of 5 stars")
        assert abs(result["score"] - 0.84) < 0.001  # 4.2/5

        # Test 10-point scale
        result = agent._fallback_parse("Score: 7.5/10")
        assert result["score"] == 0.75  # 7.5/10

        # Test percentage with score keyword
        result = agent._fallback_parse("Score: 85%")
        assert result["score"] == 0.85  # 85/100

        # Test no score found
        result = agent._fallback_parse("This code is good but could be better.")
        assert result["score"] == 0.5  # default

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_create_fallback_result(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test creating fallback result for errors."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test", artifacts={"code": "test"}, rule=rule
        )

        result = agent._create_fallback_result(request, "API Error")

        assert isinstance(result, EvalResult)
        assert result.score == 0.0
        assert "API Error" in result.comment
        assert result.passed is False
        assert result.request == request

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    @pytest.mark.asyncio
    async def test_evaluate_success(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test successful evaluation."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        # Setup mocks
        mock_agent_instance = AsyncMock()
        mock_agent.return_value = mock_agent_instance

        mock_response = MagicMock()
        mock_response.data = '{"score": 0.9, "comment": "Excellent code"}'
        mock_agent_instance.run.return_value = mock_response

        agent = EvalAgent()
        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test", artifacts={"code": "test"}, rule=rule, threshold=0.8
        )

        result = await agent.evaluate(request)

        assert isinstance(result, EvalResult)
        assert result.score == 0.9
        assert result.comment == "Excellent code"
        assert result.passed is True  # 0.9 >= 0.8
        assert result.request == request

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    @pytest.mark.asyncio
    async def test_evaluate_failure(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test evaluation with low score."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        # Setup mocks
        mock_agent_instance = AsyncMock()
        mock_agent.return_value = mock_agent_instance

        mock_response = MagicMock()
        mock_response.data = '{"score": 0.3, "comment": "Needs improvement"}'
        mock_agent_instance.run.return_value = mock_response

        agent = EvalAgent()
        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test", artifacts={"code": "test"}, rule=rule, threshold=0.8
        )

        result = await agent.evaluate(request)

        assert isinstance(result, EvalResult)
        assert result.score == 0.3
        assert result.comment == "Needs improvement"
        assert result.passed is False  # 0.3 < 0.8
        assert result.request == request

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    @pytest.mark.asyncio
    async def test_evaluate_exception_handling(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test evaluation exception handling."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        # Setup mocks
        mock_agent_instance = AsyncMock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.run.side_effect = Exception("API Error")

        agent = EvalAgent()
        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test", artifacts={"code": "test"}, rule=rule
        )

        result = await agent.evaluate(request)

        assert isinstance(result, EvalResult)
        assert result.score == 0.0
        assert "API Error" in result.comment
        assert result.passed is False
        assert result.request == request


class TestGlobalAgentFunctions:
    """Test cases for global agent functions."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_get_agent_singleton(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test that get_agent returns singleton instance."""
        # Clear any existing instance
        import numerous.pytest_llm_validate.agent
        from numerous.pytest_llm_validate.agent import EvalAgent, get_agent

        numerous.pytest_llm_validate.agent._agent_instance = None

        agent1 = get_agent()
        agent2 = get_agent()

        assert agent1 is agent2
        assert isinstance(agent1, EvalAgent)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_get_agent_creates_instance(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test that get_agent creates instance when none exists."""
        # Clear any existing instance
        import numerous.pytest_llm_validate.agent
        from numerous.pytest_llm_validate.agent import EvalAgent, get_agent

        numerous.pytest_llm_validate.agent._agent_instance = None

        agent = get_agent()

        assert isinstance(agent, EvalAgent)
        assert numerous.pytest_llm_validate.agent._agent_instance is agent


class TestAgentEdgeCases:
    """Test edge cases and error conditions."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_malformed_json(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing malformed JSON response."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        response = (
            '{"score": 0.85, "comment": "Good quality'  # Missing closing quote/brace
        )

        result = agent._parse_response(response)

        assert "score" in result
        assert "comment" in result
        assert 0.0 <= result["score"] <= 1.0

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_parse_response_invalid_score_range(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test parsing response with invalid score range."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        response = '{"score": 2.5, "comment": "Score out of range"}'

        result = agent._parse_response(response)

        # Should fallback to parsing logic
        assert "score" in result
        assert "comment" in result

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_format_artifacts_empty(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test formatting empty artifacts."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()
        artifacts = {}

        formatted = agent._format_artifacts(artifacts)

        assert formatted == ""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("numerous.pytest_llm_validate.agent.Agent")
    @patch("numerous.pytest_llm_validate.agent.OpenAIModel")
    def test_fallback_parse_edge_cases(
        self, mock_openai_model: MagicMock, mock_agent: MagicMock
    ) -> None:
        """Test fallback parsing edge cases."""
        from numerous.pytest_llm_validate.agent import EvalAgent

        agent = EvalAgent()

        # Test with very large score that should be normalized
        result = agent._fallback_parse("Score: 150")
        assert 0.0 <= result["score"] <= 1.0

        # Test with score in text but invalid format
        result = agent._fallback_parse("The score was not available")
        assert result["score"] == 0.5
