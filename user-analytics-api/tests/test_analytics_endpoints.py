def test_analytics_sales(client):
    response = client.get("/analytics/sales")
    assert response.status_code == 200
    assert response.json() == {"sales": 1000}


def test_analytics_stock(client):
    response = client.get("/analytics/stock")
    assert response.status_code == 200
    assert response.json() == {"stock": 42}
