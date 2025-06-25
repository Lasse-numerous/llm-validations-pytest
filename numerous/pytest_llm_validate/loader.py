"""Rule loader for packaged .mdc prompt files."""

import importlib.resources
import re
from pathlib import Path

from .models import EvalRule


class RuleLoader:
    """Loads and parses packaged .mdc rule files into EvalRule objects."""

    def __init__(self) -> None:
        """Initialize the rule loader."""
        self._rules_cache: dict[str, EvalRule] = {}
        self._load_packaged_rules()

    def _load_packaged_rules(self) -> None:
        """Load all packaged .mdc files from the rules directory."""
        try:
            # Use importlib.resources to access packaged files
            rules_package = "numerous.pytest_llm_validate.rules"

            rules_dir = importlib.resources.files(rules_package)
            for rule_file in rules_dir.iterdir():
                if rule_file.name.endswith(".mdc"):
                    content = rule_file.read_text(encoding="utf-8")
                    filename = rule_file.name[:-4]  # Remove .mdc extension
                    rule = self._parse_mdc_content(content, filename)
                    self._rules_cache[rule.name] = rule

        except (ImportError, AttributeError, FileNotFoundError):
            # Fallback for development/testing - try to find rules directory
            current_dir = Path(__file__).parent
            rules_dir = current_dir / "rules"

            if rules_dir.exists():
                for rule_file in rules_dir.glob("*.mdc"):
                    content = rule_file.read_text(encoding="utf-8")
                    rule = self._parse_mdc_content(content, rule_file.stem)
                    self._rules_cache[rule.name] = rule

    def _parse_mdc_content(self, content: str, filename: str) -> EvalRule:
        """Parse .mdc file content into an EvalRule object."""
        # Extract metadata from markdown headers
        metadata = self._extract_metadata(content)

        # Extract the main prompt content (everything after "## Evaluation Prompt")
        prompt = self._extract_prompt(content)

        # Extract typed values from metadata
        name = metadata.get("name", filename)
        description = metadata.get("description", "")
        version = metadata.get("version", "1.0")
        author = metadata.get("author", "pytest-llm-validate")
        tags = metadata.get("tags", [])

        # Ensure correct types for EvalRule
        name_str = name if isinstance(name, str) else filename
        description_str = description if isinstance(description, str) else ""
        version_str = version if isinstance(version, str) else "1.0"
        author_str = author if isinstance(author, str) else "pytest-llm-validate"
        tags_list = tags if isinstance(tags, list) else []

        return EvalRule(
            name=name_str,
            description=description_str,
            prompt=prompt,
            version=version_str,
            author=author_str,
            tags=tags_list,
        )

    def _extract_metadata(self, content: str) -> dict[str, str | list[str]]:
        """Extract metadata fields from the markdown content."""
        metadata: dict[str, str | list[str]] = {}

        # Pattern to match **Field:** value lines
        pattern = r"\*\*([^*]+):\*\*\s*(.+)"
        matches = re.findall(pattern, content)

        for field, value in matches:
            field_lower = field.lower().replace(" ", "_")

            if field_lower == "tags":
                # Parse comma-separated tags
                tags = [tag.strip() for tag in value.split(",")]
                metadata[field_lower] = tags
            else:
                metadata[field_lower] = value.strip()

        return metadata

    def _extract_prompt(self, content: str) -> str:
        """Extract the evaluation prompt content from the markdown."""
        # Find the "## Evaluation Prompt" section
        prompt_match = re.search(
            r"## Evaluation Prompt\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )

        if prompt_match:
            return prompt_match.group(1).strip()

        # Fallback: return everything after the first ##
        sections = content.split("##", 1)
        if len(sections) > 1:
            return sections[1].strip()

        return content.strip()

    def get_rule(self, name: str) -> EvalRule | None:
        """Get a specific rule by name."""
        return self._rules_cache.get(name)

    def get_all_rules(self) -> dict[str, EvalRule]:
        """Get all loaded rules."""
        return self._rules_cache.copy()

    def list_rule_names(self) -> list[str]:
        """Get list of all available rule names."""
        return list(self._rules_cache.keys())

    def get_default_rule(self) -> EvalRule:
        """Get the default rule (general_quality if available, otherwise first rule)."""
        if "general_quality" in self._rules_cache:
            return self._rules_cache["general_quality"]

        if self._rules_cache:
            return next(iter(self._rules_cache.values()))

        # Fallback rule if no rules loaded
        return EvalRule(
            name="fallback",
            description="Fallback rule when no packaged rules are available",
            prompt="Evaluate the given output against the specification and provide a score between 0.0 and 1.0 with explanatory comments.",
            version="1.0",
            author="pytest-llm-validate",
            tags=["fallback"],
        )


# Global loader instance
_loader_instance: RuleLoader | None = None


def get_loader() -> RuleLoader:
    """Get the global RuleLoader instance (singleton pattern)."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = RuleLoader()  # pragma: no cover
    return _loader_instance


def load_rules() -> dict[str, EvalRule]:
    """Load all packaged evaluation rules."""
    return get_loader().get_all_rules()


def get_rule(name: str) -> EvalRule | None:
    """Get a specific rule by name."""
    return get_loader().get_rule(name)


def get_default_rule() -> EvalRule:
    """Get the default evaluation rule."""
    return get_loader().get_default_rule()
