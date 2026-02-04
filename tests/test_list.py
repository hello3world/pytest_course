import pytest

def buggy_sorting_function(x:list):
    return sorted(x, key=lambda x: abs(x))

@pytest.mark.xfail(reason="The known bug")
def test_buggy_sorting_function():
    assert buggy_sorting_function([1, -1, 2, -4, 5]) == [1, -1, 2, -4, 5]
