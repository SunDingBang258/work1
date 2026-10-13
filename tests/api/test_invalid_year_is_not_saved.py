import pytest

pytestmark = pytest.mark.api
def test_cartime(client):
    response=client.post( "/api/cars",json={"year":1800})
    assert response.status_code == 422
def test_get_returns_empty_list(client):
    response=client.get("/api/cars")
    assert response.json() == []
