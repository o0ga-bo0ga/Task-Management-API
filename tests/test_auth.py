from fastapi.testclient import TestClient

def test_valid_registration(client: TestClient):
    payload = {
            "email": "prakhar@example.com",
            "password": "12345678"
            }
    response = client.post("/auth/register", json=payload)
    response_data = response.json()

    assert response.status_code == 200
    assert "id" in response_data
    
def test_duplicate_registration(client: TestClient):
    payload = {
            "email": "prakhar@example.com",
            "password": "12345678"
            }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    response_data = response.json()

    assert response.status_code == 400