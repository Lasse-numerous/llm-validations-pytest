import pytest
from numerous.pytest_llm_validate.decorator import llm_eval

def test_llm_eval_not_implemented():
    """
    Tests that the placeholder llm_eval decorator raises NotImplementedError.
    This test is expected to pass initially and will be updated when
    the decorator functionality is implemented.
    """
    @llm_eval("A simple spec")
    def sample_test_function():
        return "some output"

    with pytest.raises(NotImplementedError):
        sample_test_function()
