import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope='session')
def client():
    """Make a test api client for testing our FastAPI app."""
    with TestClient(app) as c:
        yield c


def test_analytics_sales(client):
    response = client.get("/analytics/sales")
    assert response.status_code == 200
    assert response.json() == {"sales": 1000}


def test_analytics_stock(client):
    response = client.get("/analytics/stock")
    assert response.status_code == 200
    assert response.json() == {"stock": 42}
