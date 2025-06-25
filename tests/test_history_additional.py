"""Additional tests for numerous.pytest_llm_validate.history module to improve coverage."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from numerous.pytest_llm_validate.history import (
    EvaluationHistory,
    get_history,
    reset_history_instance,
)
from numerous.pytest_llm_validate.models import EvalRequest, EvalResult, EvalRule


class TestEvaluationHistoryErrorHandling:
    """Test error handling and edge cases in EvaluationHistory."""

    def test_load_history_file_corrupted_json(self) -> None:
        """Test loading history from a corrupted JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("invalid json content {")
            temp_path = Path(f.name)

        try:
            # Should handle corrupted JSON gracefully
            history = EvaluationHistory(history_file=temp_path)
            assert history._cache == {}
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_history_file_invalid_structure(self) -> None:
        """Test loading history from a file with invalid structure."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            # Valid JSON but wrong structure (list instead of dict)
            json.dump(["not", "a", "dict"], f)
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(history_file=temp_path)
            assert history._cache == {}
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_history_file_invalid_dict_values(self) -> None:
        """Test loading history from a file with invalid dictionary values."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            # Valid JSON dict but values aren't dicts
            json.dump({"key1": "not_a_dict", "key2": 123}, f)
            temp_path = Path(f.name)

        try:
            history = EvaluationHistory(history_file=temp_path)
            assert history._cache == {}
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_history_os_error(self) -> None:
        """Test save_history when OSError occurs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            # Mock open to raise OSError
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                # Should not raise exception, just continue silently
                history._save_history()

    def test_save_history_directory_creation(self) -> None:
        """Test save_history creates parent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a nested path that doesn't exist
            nested_path = Path(temp_dir) / "nested" / "deeper" / "history.json"
            history = EvaluationHistory(history_file=nested_path)

            # Add something to cache
            history._cache["test"] = {"score": 0.8}

            # Save should create the directory structure
            history._save_history()

            assert nested_path.parent.exists()
            assert nested_path.exists()

    def test_get_cached_result_corrupted_data(self) -> None:
        """Test get_cached_result with corrupted cached data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            rule = EvalRule(name="test", description="test", prompt="test")
            request = EvalRequest(
                specification="test", artifacts={"code": "test"}, rule=rule
            )

            # Manually add corrupted data to cache
            request_hash = history._compute_hash(request)
            history._cache[request_hash] = {"invalid": "data", "missing": "fields"}

            # Should return None and clean up corrupted data
            result = history.get_cached_result(request)
            assert result is None
            assert request_hash not in history._cache

    def test_get_cached_result_key_error(self) -> None:
        """Test get_cached_result with missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            rule = EvalRule(name="test", description="test", prompt="test")
            request = EvalRequest(
                specification="test", artifacts={"code": "test"}, rule=rule
            )

            # Add data missing required fields
            request_hash = history._compute_hash(request)
            history._cache[request_hash] = {
                "score": 0.8,
                # Missing other required fields
            }

            # Should return None and clean up corrupted data
            result = history.get_cached_result(request)
            assert result is None
            assert request_hash not in history._cache


class TestArtifactNormalization:
    """Test complex artifact normalization scenarios."""

    def test_normalize_artifacts_complex_objects(self) -> None:
        """Test normalization of complex object types."""
        history = EvaluationHistory()

        artifacts = {
            "string": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "set": {1, 2, 3},
            "tuple": (1, 2, 3),
            "custom_obj": Mock(),
        }

        normalized = history._normalize_artifacts(artifacts)

        # Simple types should be preserved
        assert normalized["string"] == "hello"
        assert normalized["int"] == 42
        assert normalized["float"] == 3.14
        assert normalized["bool"] is True
        assert normalized["none"] is None

        # Complex objects should be converted to strings
        assert isinstance(normalized["list"], str)
        assert isinstance(normalized["dict"], str)
        assert isinstance(normalized["set"], str)
        assert isinstance(normalized["tuple"], str)
        assert isinstance(normalized["custom_obj"], str)

    def test_normalize_artifacts_empty_dict(self) -> None:
        """Test normalization of empty artifacts dictionary."""
        history = EvaluationHistory()
        normalized = history._normalize_artifacts({})
        assert normalized == {}

    def test_normalize_artifacts_special_values(self) -> None:
        """Test normalization of special values."""
        history = EvaluationHistory()

        artifacts = {
            "empty_string": "",
            "zero": 0,
            "false": False,
            "empty_list": [],
            "empty_dict": {},
        }

        normalized = history._normalize_artifacts(artifacts)

        assert normalized["empty_string"] == ""
        assert normalized["zero"] == 0
        assert normalized["false"] is False
        assert isinstance(normalized["empty_list"], str)
        assert isinstance(normalized["empty_dict"], str)


class TestCacheStatistics:
    """Test cache statistics computation."""

    def test_get_cache_stats_empty_cache(self) -> None:
        """Test cache statistics for empty cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            stats = history.get_cache_stats()

            assert stats["total_entries"] == 0
            assert stats["cache_file"] == str(temp_path)
            assert stats["cache_file_exists"] is False

    def test_get_cache_stats_with_entries(self) -> None:
        """Test cache statistics with entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            # Add multiple entries
            rule = EvalRule(name="test", description="test", prompt="test")

            for i in range(3):
                request = EvalRequest(
                    specification=f"test {i}",
                    artifacts={"code": f"test {i}"},
                    rule=rule,
                )
                result = EvalResult(
                    score=0.8,
                    comment="test",
                    passed=True,
                    request=request,
                    model_used="test",
                    timestamp="2024-01-01T00:00:00",
                )
                history.cache_result(result)

            stats = history.get_cache_stats()

            assert stats["total_entries"] == 3
            assert stats["cache_file"] == str(temp_path)
            assert stats["cache_file_exists"] is True
            assert stats["oldest_entry"] is not None
            assert stats["newest_entry"] is not None

    def test_get_cache_stats_entries_without_cached_at(self) -> None:
        """Test cache statistics when entries lack cached_at timestamp."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            # Manually add entries without cached_at
            history._cache["test1"] = {"score": 0.8, "comment": "test"}
            history._cache["test2"] = {"score": 0.9, "comment": "test"}

            stats = history.get_cache_stats()

            assert stats["total_entries"] == 2
            assert stats["oldest_entry"] is None
            assert stats["newest_entry"] is None


class TestGlobalHistoryInstance:
    """Test global history instance management."""

    def test_get_history_singleton(self) -> None:
        """Test that get_history returns singleton instance."""
        # Reset to ensure clean state
        reset_history_instance()

        history1 = get_history()
        history2 = get_history()

        assert history1 is history2

    def test_get_history_with_custom_file(self) -> None:
        """Test get_history with custom file path."""
        reset_history_instance()

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_history.json"

            history = get_history(history_file=custom_path)
            assert history.history_file == custom_path

    def test_get_history_subsequent_calls_ignore_file_param(self) -> None:
        """Test that subsequent calls to get_history ignore file parameter."""
        reset_history_instance()

        with tempfile.TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir) / "history1.json"
            path2 = Path(temp_dir) / "history2.json"

            history1 = get_history(history_file=path1)
            history2 = get_history(history_file=path2)  # Should be ignored

            assert history1 is history2
            assert history1.history_file == path1  # First path used

    def test_reset_history_instance(self) -> None:
        """Test resetting the global history instance."""
        # Get an instance
        history1 = get_history()

        # Reset
        reset_history_instance()

        # Get new instance
        history2 = get_history()

        # Should be different instances
        assert history1 is not history2


class TestHashingEdgeCases:
    """Test edge cases in hash computation."""

    def test_compute_hash_deterministic(self) -> None:
        """Test that hash computation is deterministic."""
        history = EvaluationHistory()

        rule = EvalRule(name="test", description="test", prompt="test")
        request = EvalRequest(
            specification="test spec",
            artifacts={"code": "test code", "output": "test output"},
            rule=rule,
            threshold=0.8,
            model="gpt-4",
            metadata={"ignored": "metadata"},
        )

        hash1 = history._compute_hash(request)
        hash2 = history._compute_hash(request)

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_compute_hash_different_for_different_requests(self) -> None:
        """Test that different requests produce different hashes."""
        history = EvaluationHistory()

        rule = EvalRule(name="test", description="test", prompt="test")

        request1 = EvalRequest(
            specification="test spec 1", artifacts={"code": "test"}, rule=rule
        )
        request2 = EvalRequest(
            specification="test spec 2", artifacts={"code": "test"}, rule=rule
        )

        hash1 = history._compute_hash(request1)
        hash2 = history._compute_hash(request2)

        assert hash1 != hash2

    def test_compute_hash_metadata_ignored(self) -> None:
        """Test that metadata is ignored in hash computation."""
        history = EvaluationHistory()

        rule = EvalRule(name="test", description="test", prompt="test")

        request1 = EvalRequest(
            specification="test",
            artifacts={"code": "test"},
            rule=rule,
            metadata={"key": "value1"},
        )
        request2 = EvalRequest(
            specification="test",
            artifacts={"code": "test"},
            rule=rule,
            metadata={"key": "value2"},
        )

        hash1 = history._compute_hash(request1)
        hash2 = history._compute_hash(request2)

        # Hashes should be the same since metadata is ignored
        assert hash1 == hash2


class TestFileSystemEdgeCases:
    """Test file system edge cases and error conditions."""

    def test_atomic_save_with_temp_file(self) -> None:
        """Test that save uses atomic replacement with temp file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"
            history = EvaluationHistory(history_file=temp_path)

            # Add data to cache
            history._cache["test"] = {"score": 0.8}

            # Mock Path.replace to verify atomic operation
            with patch("pathlib.Path.replace") as mock_replace:
                history._save_history()

                # Should call replace on the temp file
                mock_replace.assert_called_once()

    def test_load_history_os_error(self) -> None:
        """Test _load_history when file exists but can't be read."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            # Mock open to raise OSError
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                history = EvaluationHistory(history_file=temp_path)
                # Should start with empty cache despite file existing
                assert history._cache == {}
        finally:
            temp_path.unlink(missing_ok=True)
