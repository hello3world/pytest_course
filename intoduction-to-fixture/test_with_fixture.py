import pytest

@pytest.fixture
def sample_date():
    return [1, 2, 3]

def test_sum(sample_date):
    actual_sum = sum(sample_date)
    expected_sum = 6
    assert actual_sum == expected_sum, f"Expected sum of {sample_date} \
        to be {expected_sum}, but got {actual_sum}"

def test_len(sample_date):
    actual_len = len(sample_date)
    expected_len = 3
    assert actual_len == expected_len, f"Expected length of {sample_date} \
        to be {expected_len}, but got {actual_len}" 
        
@pytest.fixture
def item():
    return "an apple"

@pytest.fixture
def first_name():
    return "John"

@pytest.fixture
def last_name():
    return "Doe"

@pytest.fixture
def full_sentence(first_name, last_name, item, sample_date):
    return f"{first_name} {last_name} has {item} and numbers {sample_date}"    
        
def test_sentence_full_is_correct(full_sentence):
    expected_sentence = "John Doe has an apple and numbers [1, 2, 3]"
    assert full_sentence == expected_sentence, f"Expected sentence to be '{expected_sentence}', but got '{full_sentence}'"