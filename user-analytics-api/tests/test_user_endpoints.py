import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope='session')
def client():
    """Make a test api client for testing our FastAPI app."""
    with TestClient(app) as c:
        yield c


def test_user_profile(client):
    response = client.get("/user/123/profile")
    assert response.status_code == 200
    assert response.json() == {"user_id": 123, "profile": "UserProfileData"}


def test_user_files(client):
    response = client.get("/user/123/files")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": 123,
        "files": ["file1.txt", "file2.txt"]
    }
