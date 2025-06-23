import pathlib
import frontmatter
import logging
from typing import Dict, Optional

from .model import EvalRule

logger = logging.getLogger(__name__)

_cached_rules: Optional[Dict[str, EvalRule]] = None

def load_rules(prompts_dir: Optional[pathlib.Path] = None) -> Dict[str, EvalRule]:
    """
    Loads all evaluation rules from .mdc files in the specified prompts directory.

    Rules are parsed for YAML frontmatter (metadata) and Markdown content (prompt template).
    Results are cached globally after the first successful load for a given directory.

    Args:
        prompts_dir: Optional path to the directory containing .mdc files.
                     If None, defaults to a 'prompts' subdirectory relative to this file.

    Returns:
        A dictionary of EvalRule objects, keyed by their rule ID.
        Returns an empty dictionary if the prompts directory doesn't exist or is empty.
    """
    global _cached_rules
    # TODO: Cache invalidation if prompts_dir changes or files are modified in dev.
    # For now, simple global cache. If prompts_dir is None, it implies a default path.
    if _cached_rules is not None and prompts_dir is None: # Only use cache if default path was used
        return _cached_rules

    if prompts_dir is None:
        base_path = pathlib.Path(__file__).parent
        prompts_dir = base_path / "prompts"

    if not prompts_dir.is_dir():
        logger.warning(
            f"Prompts directory not found: {prompts_dir}. No rules will be loaded."
        )
        return {}

    loaded_rules: Dict[str, EvalRule] = {}
    for mdc_file in prompts_dir.glob("*.mdc"):
        try:
            rule_content = frontmatter.load(mdc_file)
            metadata = rule_content.metadata

            rule_id = metadata.get("id", mdc_file.stem) # Use filename stem if id not in frontmatter

            if not metadata.get("name"):
                logger.warning(f"Rule file {mdc_file.name} is missing 'name' in frontmatter. Skipping.")
                continue
            if not metadata.get("description"):
                logger.warning(f"Rule file {mdc_file.name} is missing 'description' in frontmatter. Skipping.")
                continue
            if not rule_content.content:
                logger.warning(f"Rule file {mdc_file.name} has no content for prompt_template. Skipping.")
                continue


            rule = EvalRule(
                id=rule_id,
                name=metadata["name"],
                description=metadata["description"],
                prompt_template=rule_content.content,
            )
            if rule.id in loaded_rules:
                logger.warning(
                    f"Duplicate rule ID '{rule.id}' found in {mdc_file.name}. "
                    f"Overwriting rule from {loaded_rules[rule.id].name}."
                )
            loaded_rules[rule.id] = rule
            logger.debug(f"Successfully loaded rule '{rule.id}' from {mdc_file.name}")

        except Exception as e:
            logger.error(f"Error loading rule from {mdc_file.name}: {e}", exc_info=True)
            # Continue to try loading other files

    if prompts_dir is None: # Cache only if default path was used
      _cached_rules = loaded_rules
    return loaded_rules

# Example of how to get a specific rule, can be expanded later
def get_rule(rule_id: str, prompts_dir: Optional[pathlib.Path] = None) -> Optional[EvalRule]:
    """
    Retrieves a specific rule by its ID.
    Loads rules if they haven't been loaded yet for the given prompts_dir.
    """
    rules = load_rules(prompts_dir)
    return rules.get(rule_id)

if __name__ == "__main__":
    # Basic test loading
    logging.basicConfig(level=logging.DEBUG)
    rules = load_rules()
    if rules:
        print(f"Loaded {len(rules)} rule(s):")
        for rule_id, rule in rules.items():
            print(f"  ID: {rule_id}, Name: {rule.name}")
            # print(f"    Description: {rule.description}")
            # print(f"    Template: \n{rule.prompt_template[:100]}...") # Print first 100 chars
        retrieved_rule = get_rule("default_eval")
        if retrieved_rule:
            print(f"\nSuccessfully retrieved 'default_eval' rule: {retrieved_rule.name}")
    else:
        print("No rules loaded.")
