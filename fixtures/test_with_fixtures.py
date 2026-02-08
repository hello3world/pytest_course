import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    expected_sum = 15
    actual_sum = sum(sample_data) 
    assert actual_sum == expected_sum

def test_len(sample_data):
    expected_length = 5
    actual_length = len(sample_data)
    assert actual_length == expected_length
    
@pytest.fixture
def first_name():
    return "John"

@pytest.fixture
def last_name():
    return "Doe"

@pytest.fixture
def full_sentence(first_name, last_name):
    return f"My name is {first_name} {last_name}"

def test_sentence_full_is_corect(full_sentence):
    expected_sentence = "My name is John Doe"
    assert full_sentence == expected_sentence

def test_sentence_has_word_has(full_sentence):
    assert "name" in full_sentence

@pytest.fixture
def number():
    return 42

def test_number(number):
    assert number == 42
