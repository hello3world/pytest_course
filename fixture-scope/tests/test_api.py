import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
    assert response.json()["message"] == "pong"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# pytest fixture-scope\tests\test_api.py -v --setup-show