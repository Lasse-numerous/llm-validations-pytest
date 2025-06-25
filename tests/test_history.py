"""Tests for the history and deduplication functionality."""

import tempfile
from pathlib import Path

from numerous.pytest_llm_validate.history import (
    EvaluationHistory,
    get_history,
    reset_history_instance,
)
from numerous.pytest_llm_validate.loader import get_default_rule
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult


class TestEvaluationHistory:
    """Test cases for EvaluationHistory class."""

    def setup_method(self) -> None:
        """Set up each test method."""
        # Reset global instance for clean tests
        reset_history_instance()

    def test_history_creation_with_temp_file(self) -> None:
        """Test creating history with a temporary file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)
            assert history.history_file == temp_path
            assert len(history._cache) == 0
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_history_creation_default_location(self) -> None:
        """Test creating history with default location."""
        history = EvaluationHistory()
        expected_path = Path.cwd() / ".pytest-llm-validate-history.json"
        assert history.history_file == expected_path

    def test_cache_and_retrieve_result(self) -> None:
        """Test caching and retrieving evaluation results."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)

            # Create a test request and result
            rule = get_default_rule()
            request = EvalRequest(
                specification="Test specification",
                artifacts={"output": "test output"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            result = EvalResult(
                score=0.8,
                comment="Good output",
                passed=True,
                request=request,
                model_used="gpt-4o-mini",
                timestamp="2024-01-01T00:00:00",
            )

            # Cache the result
            history.cache_result(result)

            # Retrieve the cached result
            cached_result = history.get_cached_result(request)
            assert cached_result is not None
            assert cached_result.score == 0.8
            assert cached_result.comment == "Good output"
            assert cached_result.passed is True

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_hash_computation_deterministic(self) -> None:
        """Test that hash computation is deterministic."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)
            rule = get_default_rule()

            # Create identical requests
            request1 = EvalRequest(
                specification="Test spec",
                artifacts={"output": "test"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            request2 = EvalRequest(
                specification="Test spec",
                artifacts={"output": "test"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            # Hash should be identical
            hash1 = history._compute_hash(request1)
            hash2 = history._compute_hash(request2)
            assert hash1 == hash2

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_hash_different_for_different_requests(self) -> None:
        """Test that different requests produce different hashes."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)
            rule = get_default_rule()

            request1 = EvalRequest(
                specification="Test spec 1",
                artifacts={"output": "test"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            request2 = EvalRequest(
                specification="Test spec 2",  # Different specification
                artifacts={"output": "test"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            hash1 = history._compute_hash(request1)
            hash2 = history._compute_hash(request2)
            assert hash1 != hash2

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_persistence_across_instances(self) -> None:
        """Test that cached results persist across history instances."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            # Create first history instance and cache a result
            history1 = EvaluationHistory(temp_path)
            rule = get_default_rule()

            request = EvalRequest(
                specification="Persistent test",
                artifacts={"output": "test output"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            result = EvalResult(
                score=0.9,
                comment="Excellent",
                passed=True,
                request=request,
                model_used="gpt-4o-mini",
                timestamp="2024-01-01T00:00:00",
            )

            history1.cache_result(result)

            # Create second history instance and check if result is still there
            history2 = EvaluationHistory(temp_path)
            cached_result = history2.get_cached_result(request)

            assert cached_result is not None
            assert cached_result.score == 0.9
            assert cached_result.comment == "Excellent"

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_clear_cache(self) -> None:
        """Test clearing the evaluation cache."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)
            rule = get_default_rule()

            # Add a cached result
            request = EvalRequest(
                specification="Test to clear",
                artifacts={"output": "test"},
                rule=rule,
                threshold=0.7,
                model="gpt-4o-mini",
            )

            result = EvalResult(
                score=0.8,
                comment="Good",
                passed=True,
                request=request,
                model_used="gpt-4o-mini",
                timestamp="2024-01-01T00:00:00",
            )

            history.cache_result(result)
            assert history.get_cached_result(request) is not None

            # Clear cache
            history.clear_cache()
            assert history.get_cached_result(request) is None

            # Verify persistence of clear
            history2 = EvaluationHistory(temp_path)
            assert history2.get_cached_result(request) is None

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_cache_stats(self) -> None:
        """Test getting cache statistics."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)

            # Test empty cache stats
            stats = history.get_cache_stats()
            assert stats["total_entries"] == 0
            assert stats["cache_file"] == str(temp_path)

            # Add some entries
            rule = get_default_rule()

            for i in range(3):
                request = EvalRequest(
                    specification=f"Test {i}",
                    artifacts={"output": f"output {i}"},
                    rule=rule,
                    threshold=0.7,
                    model="gpt-4o-mini",
                )

                result = EvalResult(
                    score=0.8,
                    comment="Good",
                    passed=True,
                    request=request,
                    model_used="gpt-4o-mini",
                    timestamp="2024-01-01T00:00:00",
                )

                history.cache_result(result)

            # Check updated stats
            stats = history.get_cache_stats()
            assert stats["total_entries"] == 3
            assert "oldest_entry" in stats
            assert "newest_entry" in stats

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_corrupted_cache_file_handling(self) -> None:
        """Test handling of corrupted cache files."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            # Write corrupted JSON
            with open(temp_path, "w") as f:
                f.write("{ invalid json")

            # Should handle gracefully
            history = EvaluationHistory(temp_path)
            assert len(history._cache) == 0

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_global_history_instance(self) -> None:
        """Test the global history instance management."""
        reset_history_instance()

        # First call should create instance
        history1 = get_history()
        assert history1 is not None

        # Second call should return same instance
        history2 = get_history()
        assert history1 is history2

        # Reset and create new instance
        reset_history_instance()
        history3 = get_history()
        assert history3 is not history1

    def test_normalize_artifacts(self) -> None:
        """Test artifact normalization for consistent hashing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(temp_path)

            # Test various artifact types
            artifacts = {
                "string": "test",
                "integer": 42,
                "float": 3.14,
                "boolean": True,
                "none": None,
                "complex": {"nested": "dict"},
                "list": [1, 2, 3],
            }

            normalized = history._normalize_artifacts(artifacts)

            # Check types are normalized
            assert isinstance(normalized["string"], str)
            assert isinstance(normalized["integer"], int)
            assert isinstance(normalized["float"], float)
            assert isinstance(normalized["boolean"], bool)
            assert normalized["none"] is None
            assert isinstance(
                normalized["complex"], str
            )  # Should be converted to string
            assert isinstance(normalized["list"], str)  # Should be converted to string

        finally:
            if temp_path.exists():
                temp_path.unlink()
