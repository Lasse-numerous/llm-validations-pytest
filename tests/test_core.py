import pytest
from numerous.pytest_llm_validate.core import load_rules

def test_loader_missing_raises():
    """
    Tests that the placeholder load_rules function raises NotImplementedError.
    This test is expected to pass initially and will be updated when
    the loader functionality is implemented.
    """
    with pytest.raises(NotImplementedError):
        load_rules()
