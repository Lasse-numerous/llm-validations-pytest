"""History and deduplication system for pytest-llm-validate."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import EvalRequest, EvalResult


class EvaluationHistory:
    """Manages history and deduplication of evaluations."""

    def __init__(self, history_file: Path | None = None) -> None:
        """Initialize the evaluation history.

        Args:
            history_file: Path to the history JSON file. If None, uses default location.
        """
        if history_file is None:
            # Default to .pytest-llm-validate-history.json in current directory
            self.history_file = Path.cwd() / ".pytest-llm-validate-history.json"
        else:
            self.history_file = history_file

        self._cache: dict[str, dict[str, Any]] = {}
        self._load_history()

    def _load_history(self) -> None:
        """Load evaluation history from the JSON file."""
        if not self.history_file.exists():
            self._cache = {}
            return

        try:
            with open(self.history_file, encoding="utf-8") as f:
                data = json.load(f)
                # Validate the structure
                if isinstance(data, dict) and all(
                    isinstance(v, dict) for v in data.values()
                ):
                    self._cache = data
                else:
                    # Invalid format, start fresh
                    self._cache = {}
        except (json.JSONDecodeError, OSError):
            # Corrupted or unreadable file, start fresh
            self._cache = {}

    def _save_history(self) -> None:
        """Save evaluation history to the JSON file."""
        try:
            # Create parent directory if it doesn't exist
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # Save atomically by writing to temp file first
            temp_file = self.history_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)

            # Atomic replace
            temp_file.replace(self.history_file)
        except OSError:
            # If we can't save, that's not fatal - just continue without persistence
            pass

    def _compute_hash(self, request: EvalRequest) -> str:
        """Compute a hash for the evaluation request for deduplication.

        Args:
            request: The evaluation request to hash

        Returns:
            Hexadecimal hash string
        """
        # Create a deterministic representation of the request
        hash_data = {
            "specification": request.specification,
            "artifacts": self._normalize_artifacts(request.artifacts),
            "rule_name": request.rule.name,
            "rule_prompt": request.rule.prompt,
            "threshold": request.threshold,
            "model": request.model,
            # Don't include metadata as it shouldn't affect the evaluation logic
        }

        # Convert to JSON string with sorted keys for deterministic hashing
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)

        # Compute SHA-256 hash
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def _normalize_artifacts(self, artifacts: dict[str, Any]) -> dict[str, Any]:
        """Normalize artifacts for consistent hashing.

        Args:
            artifacts: The artifacts dictionary to normalize

        Returns:
            Normalized artifacts dictionary
        """
        normalized: dict[str, Any] = {}

        for key, value in artifacts.items():
            # Convert various types to strings for consistent hashing
            if isinstance(value, str | int | float | bool):
                normalized[key] = value
            elif value is None:
                normalized[key] = None
            else:
                # Convert complex objects to string representation
                normalized[key] = str(value)

        return normalized

    def get_cached_result(self, request: EvalRequest) -> EvalResult | None:
        """Get a cached evaluation result if it exists.

        Args:
            request: The evaluation request to look up

        Returns:
            Cached result if found, None otherwise
        """
        request_hash = self._compute_hash(request)

        if request_hash not in self._cache:
            return None

        cached_data = self._cache[request_hash]

        try:
            # Reconstruct EvalResult from cached data
            result = EvalResult(
                score=cached_data["score"],
                comment=cached_data["comment"],
                passed=cached_data["passed"],
                request=request,  # Use the current request object
                model_used=cached_data["model_used"],
                timestamp=cached_data["timestamp"],
            )
            return result
        except (KeyError, TypeError):
            # Cached data is corrupted, remove it
            del self._cache[request_hash]
            return None

    def cache_result(self, result: EvalResult) -> None:
        """Cache an evaluation result for future deduplication.

        Args:
            result: The evaluation result to cache
        """
        request_hash = self._compute_hash(result.request)

        # Store the result data
        self._cache[request_hash] = {
            "score": result.score,
            "comment": result.comment,
            "passed": result.passed,
            "model_used": result.model_used,
            "timestamp": result.timestamp,
            "cached_at": datetime.now().isoformat(),
        }

        # Save to disk
        self._save_history()

    def clear_cache(self) -> None:
        """Clear all cached evaluation results."""
        self._cache.clear()
        self._save_history()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get statistics about the evaluation cache.

        Returns:
            Dictionary with cache statistics
        """
        if not self._cache:
            return {
                "total_entries": 0,
                "cache_file": str(self.history_file),
                "cache_file_exists": self.history_file.exists(),
            }

        # Analyze cache contents
        timestamps = []
        for entry in self._cache.values():
            if "cached_at" in entry:
                timestamps.append(entry["cached_at"])

        return {
            "total_entries": len(self._cache),
            "cache_file": str(self.history_file),
            "cache_file_exists": self.history_file.exists(),
            "oldest_entry": min(timestamps) if timestamps else None,
            "newest_entry": max(timestamps) if timestamps else None,
        }


# Global history instance
_history_instance: EvaluationHistory | None = None


def get_history(history_file: Path | None = None) -> EvaluationHistory:
    """Get the global EvaluationHistory instance.

    Args:
        history_file: Optional path to history file (only used on first call)

    Returns:
        EvaluationHistory instance
    """
    global _history_instance
    if _history_instance is None:
        _history_instance = EvaluationHistory(history_file)
    return _history_instance


def reset_history_instance() -> None:
    """Reset the global history instance (mainly for testing)."""
    global _history_instance
    _history_instance = None
