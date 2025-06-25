"""Tests for numerous.pytest_llm_validate.plugin module."""

import logging
import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

from numerous.pytest_llm_validate.plugin import (
    pytest_configure,
    pytest_unconfigure,
)


class TestPytestConfigure:
    """Test cases for pytest_configure function."""

    def test_configure_default_logging(self) -> None:
        """Test default logging configuration."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            pytest_configure(mock_config)

            # Verify logger was configured
            mock_get_logger.assert_called_with("pytest_llm_validate")
            mock_logger.setLevel.assert_called_with(logging.INFO)
            mock_logger.addHandler.assert_called_once()
            assert mock_logger.propagate is False

    def test_configure_verbose_logging(self) -> None:
        """Test verbose logging configuration."""
        mock_config = MagicMock()
        mock_config.option.verbose = 2

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            pytest_configure(mock_config)

            # Verify DEBUG level was set for high verbosity
            mock_logger.setLevel.assert_called_with(logging.DEBUG)

    def test_configure_single_verbose_logging(self) -> None:
        """Test single verbose logging configuration."""
        mock_config = MagicMock()
        mock_config.option.verbose = 1

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            pytest_configure(mock_config)

            # Verify INFO level was set for single verbosity
            mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_configure_no_verbose_attribute(self) -> None:
        """Test configuration when verbose attribute is missing."""
        mock_config = MagicMock()
        del mock_config.option.verbose  # Remove verbose attribute

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            pytest_configure(mock_config)

            # Should fall back to INFO level
            mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_configure_env_var_log_level(self) -> None:
        """Test log level from environment variable."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0

        with patch.dict(os.environ, {"PYTEST_LLM_VALIDATE_LOG_LEVEL": "DEBUG"}):
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []

                pytest_configure(mock_config)

                # Verify DEBUG level from env var
                mock_logger.setLevel.assert_called_with(logging.DEBUG)

    def test_configure_invalid_env_log_level(self) -> None:
        """Test invalid log level from environment variable."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0

        with patch.dict(os.environ, {"PYTEST_LLM_VALIDATE_LOG_LEVEL": "INVALID"}):
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []

                pytest_configure(mock_config)

                # Should fall back to INFO level
                mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_configure_existing_handlers(self) -> None:
        """Test configuration when logger already has handlers."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = [MagicMock()]  # Already has handlers

            pytest_configure(mock_config)

            # Should not add new handler
            mock_logger.addHandler.assert_not_called()

    def test_configure_handler_format(self) -> None:
        """Test that handler is configured with correct format."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            with patch("logging.StreamHandler") as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler_class.return_value = mock_handler

                with patch("logging.Formatter") as mock_formatter_class:
                    mock_formatter = MagicMock()
                    mock_formatter_class.return_value = mock_formatter

                    pytest_configure(mock_config)

                    # Verify handler setup
                    mock_handler_class.assert_called_once_with(sys.stdout)
                    mock_formatter_class.assert_called_once_with(
                        "[LLM-VALIDATE] %(levelname)s: %(message)s"
                    )
                    mock_handler.setFormatter.assert_called_once_with(mock_formatter)
                    mock_logger.addHandler.assert_called_once_with(mock_handler)


class TestPytestUnconfigure:
    """Test cases for pytest_unconfigure function."""

    def test_unconfigure_logs_completion(self) -> None:
        """Test that unconfigure logs completion message."""
        mock_config = MagicMock()

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            pytest_unconfigure(mock_config)

            # Verify completion message was logged
            mock_get_logger.assert_called_with("pytest_llm_validate")
            mock_logger.info.assert_called_with("LLM validation session completed")


class TestLLMEvalFixture:
    """Test cases for llm_eval fixture."""

    def test_llm_eval_fixture_returns_callable(self, llm_eval: Any) -> None:
        """Test that llm_eval fixture returns a callable."""
        assert callable(llm_eval)

    def test_llm_eval_fixture_is_create_llm_eval_tester(self, llm_eval: Any) -> None:
        """Test that llm_eval fixture returns create_llm_eval_tester."""
        from numerous.pytest_llm_validate.fixture import create_llm_eval_tester

        assert llm_eval is create_llm_eval_tester

    def test_llm_eval_fixture_can_be_called(self, llm_eval: Any) -> None:
        """Test that the fixture result can be called with specification."""
        # This should not raise an exception
        tester = llm_eval("Test specification")
        assert tester is not None


class TestPluginIntegration:
    """Integration tests for the plugin."""

    def test_plugin_configure_unconfigure_cycle(self) -> None:
        """Test complete configure/unconfigure cycle."""
        mock_config = MagicMock()
        mock_config.option.verbose = 1

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            # Configure
            pytest_configure(mock_config)

            # Verify configure was called
            assert mock_get_logger.call_count >= 1

            # Unconfigure
            pytest_unconfigure(mock_config)

            # Verify unconfigure was called
            mock_logger.info.assert_called_with("LLM validation session completed")

    def test_plugin_with_different_verbosity_levels(self) -> None:
        """Test plugin with different verbosity levels."""
        test_cases = [
            (0, logging.INFO),
            (1, logging.INFO),
            (2, logging.DEBUG),
            (3, logging.DEBUG),
        ]

        for verbosity, expected_level in test_cases:
            mock_config = MagicMock()
            mock_config.option.verbose = verbosity

            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []

                pytest_configure(mock_config)

                mock_logger.setLevel.assert_called_with(expected_level)

    def test_plugin_env_var_overrides_verbosity(self) -> None:
        """Test that environment variable overrides verbosity setting."""
        mock_config = MagicMock()
        mock_config.option.verbose = 0  # Low verbosity

        with patch.dict(os.environ, {"PYTEST_LLM_VALIDATE_LOG_LEVEL": "DEBUG"}):
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []

                pytest_configure(mock_config)

                # Should use DEBUG from env var, not INFO from low verbosity
                mock_logger.setLevel.assert_called_with(logging.DEBUG)
