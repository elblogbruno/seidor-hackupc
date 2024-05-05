from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "price" in response.json()

def test_post_item():
    response = client.post("/items", json={"name": "Test Item", "price": 10.0})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
    assert response.json()["price"] == 10.0