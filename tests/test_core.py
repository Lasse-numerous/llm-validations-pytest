import pytest
import pathlib
import logging
from unittest import mock

from numerous.pytest_llm_validate.core import load_rules, get_rule, _cached_rules
from numerous.pytest_llm_validate.model import EvalRule

# Helper to reset the global cache before each test function if needed
@pytest.fixture(autouse=True)
def reset_rule_cache():
    global _cached_rules
    _cached_rules = None

@pytest.fixture
def sample_prompts_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Creates a temporary prompts directory with sample .mdc files."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Valid rule file
    valid_rule_content = """---
id: rule1
name: Rule One
description: This is the first rule.
---
This is the prompt template for Rule One.
Input: {input}
"""
    (prompts_dir / "rule1.mdc").write_text(valid_rule_content)

    # Another valid rule, ID from filename
    rule2_content = """---
name: Rule Two From Filename
description: This is the second rule, ID from filename.
---
This is the prompt template for Rule Two.
Specification: {user_specification}
"""
    (prompts_dir / "rule2_from_filename.mdc").write_text(rule2_content)


    # Rule missing name
    missing_name_content = """---
id: rule_missing_name
description: This rule is missing its name.
---
Prompt content.
"""
    (prompts_dir / "rule_missing_name.mdc").write_text(missing_name_content)

    # Rule with duplicate ID
    duplicate_id_content = """---
id: rule1
name: Rule One Duplicate
description: This rule has a duplicate ID.
---
This is a duplicate prompt.
"""
    (prompts_dir / "duplicate_id_rule.mdc").write_text(duplicate_id_content)

    return prompts_dir

def test_load_rules_finds_sample_rules(sample_prompts_dir: pathlib.Path):
    """Tests that load_rules correctly loads valid .mdc files."""
    rules = load_rules(prompts_dir=sample_prompts_dir)

    assert "rule1" in rules
    rule1 = rules["rule1"]
    assert isinstance(rule1, EvalRule)
    assert rule1.id == "rule1"
    assert rule1.name == "Rule One"
    assert rule1.description == "This is the first rule."
    assert rule1.prompt_template.strip() == "This is the prompt template for Rule One.\nInput: {input}"

    assert "rule2_from_filename" in rules # ID derived from filename
    rule2 = rules["rule2_from_filename"]
    assert isinstance(rule2, EvalRule)
    assert rule2.id == "rule2_from_filename"
    assert rule2.name == "Rule Two From Filename"

def test_load_rules_returns_dict(sample_prompts_dir: pathlib.Path):
    """Tests that the return type is a dictionary and keys match rule IDs."""
    rules = load_rules(prompts_dir=sample_prompts_dir)
    assert isinstance(rules, dict)
    for rule_id, rule_obj in rules.items():
        assert rule_id == rule_obj.id
        assert isinstance(rule_obj, EvalRule)

def test_load_rules_no_prompts_dir(tmp_path: pathlib.Path, caplog):
    """Tests behavior when the prompts directory does not exist."""
    non_existent_dir = tmp_path / "does_not_exist"
    with caplog.at_level(logging.WARNING):
        rules = load_rules(prompts_dir=non_existent_dir)

    assert not rules # Should be an empty dict
    assert f"Prompts directory not found: {non_existent_dir}" in caplog.text

def test_load_rules_empty_prompts_dir(tmp_path: pathlib.Path):
    """Tests behavior with an empty prompts directory."""
    empty_dir = tmp_path / "empty_prompts"
    empty_dir.mkdir()
    rules = load_rules(prompts_dir=empty_dir)
    assert not rules

def test_load_rules_skips_file_missing_metadata(sample_prompts_dir: pathlib.Path, caplog):
    """Tests that rules missing essential metadata are skipped with a warning."""
    with caplog.at_level(logging.WARNING):
        rules = load_rules(prompts_dir=sample_prompts_dir)

    assert "rule_missing_name" not in rules
    assert "is missing 'name' in frontmatter. Skipping." in caplog.text
    # Check that rule1 (valid) is still loaded
    assert "rule1" in rules

def test_load_rules_handles_duplicate_id(sample_prompts_dir: pathlib.Path, caplog):
    """Tests that duplicate rule IDs are handled (last one wins) with a warning."""
    with caplog.at_level(logging.WARNING):
        rules = load_rules(prompts_dir=sample_prompts_dir)

    assert "rule1" in rules
    # The duplicate_id_rule.mdc also has id: rule1. The original rule1.mdc should be loaded first.
    # Depending on glob order, one might overwrite the other. The test ensures 'rule1' exists.
    # And that a warning about duplication is logged.
    assert "Duplicate rule ID 'rule1' found" in caplog.text
    # We expect one of them to be present.
    # If 'duplicate_id_rule.mdc' (name: Rule One Duplicate) overwrites 'rule1.mdc' (name: Rule One)
    assert rules["rule1"].name == "Rule One Duplicate" # Assuming duplicate_id_rule.mdc is processed after rule1.mdc

def test_get_rule_loads_and_retrieves(sample_prompts_dir: pathlib.Path):
    """Tests get_rule successfully retrieves a specific rule."""
    rule = get_rule("rule1", prompts_dir=sample_prompts_dir)
    assert rule is not None
    assert rule.id == "rule1"
    assert rule.name == "Rule One"

    non_existent_rule = get_rule("non_existent_id", prompts_dir=sample_prompts_dir)
    assert non_existent_rule is None

def test_load_rules_uses_default_path_if_none_provided(monkeypatch):
    """
    Tests that load_rules uses the default 'prompts' directory
    next to core.py if no directory is specified.
    This test assumes there's a 'prompts/default_eval.mdc' relative to core.py.
    """
    # To make this test robust, we mock the actual file loading part for the default path
    # and just check that the path calculation leads to the expected default path.

    mock_rules_dict = {"default_eval": mock.MagicMock(spec=EvalRule, id="default_eval")}

    # We need to mock pathlib.Path.glob to control what files are "found"
    # and frontmatter.load to control what is "parsed"
    # This makes the test independent of the actual default_eval.mdc file content during this specific unit test
    # The actual content of default_eval.mdc is tested by other tests using sample_prompts_dir

    # Path to the expected default prompts directory
    expected_default_prompts_dir = pathlib.Path(__file__).parent.parent / "numerous/pytest_llm_validate/prompts"

    # Mocking glob to simulate finding 'default_eval.mdc'
    mock_glob_results = [expected_default_prompts_dir / "default_eval.mdc"]

    # Mocking frontmatter.load
    mock_post = mock.MagicMock()
    mock_post.metadata = {'id': 'default_eval', 'name': 'Default Rule', 'description': 'A default rule.'}
    mock_post.content = "Default prompt template."

    with mock.patch('pathlib.Path.glob', return_value=mock_glob_results) as mock_glob, \
         mock.patch('frontmatter.load', return_value=mock_post) as mock_fm_load:

        # Patch is_dir for the default path to ensure it's seen as a directory
        with mock.patch('pathlib.Path.is_dir', return_value=True) as mock_is_dir:
            rules = load_rules(prompts_dir=None) # Call with None to trigger default path logic

            # Check that is_dir was called with the expected default path
            # The first call to is_dir is on the prompts_dir itself.
            assert mock_is_dir.call_args_list[0].args[0].resolve() == expected_default_prompts_dir.resolve()

            # Check that glob was called on the expected default path
            # The Path object used in glob might be slightly different due to how it's constructed,
            # so we check the parent of the first glob result.
            assert mock_glob.call_args[0][0].parent.resolve() == expected_default_prompts_dir.resolve()

            # Check that frontmatter.load was called with the file from the default dir
            mock_fm_load.assert_called_once_with(expected_default_prompts_dir / "default_eval.mdc")

    assert "default_eval" in rules
    assert rules["default_eval"].name == "Default Rule"


def test_load_rules_caching_behavior(sample_prompts_dir: pathlib.Path):
    """Tests that rules are cached on subsequent calls with default path."""
    global _cached_rules
    _cached_rules = None # Ensure cache is clear

    # First call, should load and cache (if default path was used)
    # For this test, let's simulate it being called with the default path logic
    # by first loading with a specific path, then with None.

    # To test caching with the *default* path, we first need to ensure
    # the default path is actually used. The current `load_rules` only caches
    # if `prompts_dir` is `None`.

    # For this test, we will mock the default path to be our sample_prompts_dir
    # to control the environment precisely for caching.

    default_path_target = "numerous.pytest_llm_validate.core.pathlib.Path"

    with mock.patch(f"{default_path_target}.__new__") as mock_path_constructor:
        # Configure the mock Path object that __file__.parent would return
        # such that when .parent and / "prompts" is called, it resolves to sample_prompts_dir
        mock_base_path_obj = mock.MagicMock(spec=pathlib.Path)
        mock_base_path_obj / "prompts" = sample_prompts_dir # This makes (Path(__file__).parent / "prompts") yield sample_prompts_dir

        # The Path() constructor will be called for pathlib.Path(__file__)
        # We want Path(__file__) to yield a path whose parent is mock_base_path_obj
        mock_file_path_obj = mock.MagicMock(spec=pathlib.Path)
        mock_file_path_obj.parent = mock_base_path_obj

        # Make Path() return our mock_file_path_obj when it's likely being used for __file__
        # This is a bit indirect; a more direct mock of `pathlib.Path(__file__).parent` might be better if possible.
        # For now, we assume the first Path construction inside load_rules (when prompts_dir is None) is for __file__.
        mock_path_constructor.return_value = mock_file_path_obj

        # First call with prompts_dir=None, should load from (mocked) default and cache
        rules1 = load_rules(prompts_dir=None)
        assert "rule1" in rules1
        assert _cached_rules is not None
        assert _cached_rules == rules1 # Cache should be populated

        # To verify caching, we can try to load from a non-existent directory for the *second* call,
        # but if caching works, it should return the cached `rules1`.
        # However, `load_rules` only uses cache if `prompts_dir` is None.
        # So, we need to ensure `frontmatter.load` is NOT called again if cache is hit.

        with mock.patch("numerous.pytest_llm_validate.core.frontmatter.load") as mock_frontmatter_load:
            rules2 = load_rules(prompts_dir=None) # Second call with None
            mock_frontmatter_load.assert_not_called() # Should not load files again due to cache
            assert rules2 == rules1 # Should return cached rules

    # Test that cache is NOT used if a specific prompts_dir is provided
    _cached_rules = {"cached_rule": mock.MagicMock(spec=EvalRule)} # Pre-populate cache

    # Call with a specific (valid) directory. It should bypass the cache.
    rules_specific_dir = load_rules(prompts_dir=sample_prompts_dir)
    assert "rule1" in rules_specific_dir # Loaded from sample_prompts_dir
    assert "cached_rule" not in rules_specific_dir # Not from cache

    # Ensure cache was not overwritten by the specific path load
    assert "cached_rule" in _cached_rules

# Clean up cache after all tests in this module
def teardown_module(module):
    global _cached_rules
    _cached_rules = None
