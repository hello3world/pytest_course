import pytest
import os

@pytest.fixture
def temp_file():
    file_path = "fixtures/temp_file.txt"
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("This is a temporary file.")
    yield file_path
    
    # Tear down logic
    os.remove(file_path)

def test_file_starts_with_name(temp_file):
    content = open(temp_file, "r").read()
    assert content == "This is a temporary file."
    
def test_file_write_task(temp_file):
    with open(temp_file, "a") as file:
        file.write("\nThis is a new line.")
    content = open(temp_file, "r").read()
    assert content == "This is a temporary file.\nThis is a new line."
# pytest fixtures\test_with_fixtures.py
