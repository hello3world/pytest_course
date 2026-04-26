import pytest 
import os


@pytest.fixture
def temp_file():
    file_path = "temp_notes_file.txt"
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("Initial content\n")
    yield file_path
    
    # Teardown: remove the file after the test
    if os.path.exists(file_path):
        os.remove(file_path)

def test_file_starts_with_name(temp_file):
    with open(temp_file, "r") as f:
        content = f.read()
    assert content.startswith("Initial"), f"Expected file content to start with 'Initial', but got '{content}'"
    
def test_file_write_task(temp_file):
    with open(temp_file, "a") as f:
        f.write("Additional content\n")
    with open(temp_file, "r") as f:
        content = f.read()
    assert content == "Initial content\nAdditional content\n"