def test_sum():
    assert 1 + 5 == 6

def test_subtract():
    assert 1 - 1 == 0

def test_comparing_lists():
    assert [1, 2, 3] == [1, 3, 2]

class TestClass:
    def test_sum(self):
        assert 1 + 7 == 6

    def test_subtract(self):
        assert 1 - 1 == 0

    def test_comparing_lists(self):
        assert [1, 2, 3] == [1, 2, 3]
