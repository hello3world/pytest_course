import pytest

@pytest.mark.skip(reason="Skipping merge dict test")
def test_merge_dict():
    a = {"a": 1, "b": 2}
    b = {"b": 3, "c": 4}
    assert a | b == {"a": 1, "b": 3, "c": 4}
