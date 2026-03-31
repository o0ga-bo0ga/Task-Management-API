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

def test_successful_login(client: TestClient):
    registration_payload = {
            "email": "prakhar@example.com",
            "password": "12345678"
            }
    client.post("/auth/register", json=registration_payload)

    login_payload = {
            "username": "prakhar@example.com",
            "password": "12345678"
            }
    response = client.post("/auth/login", data=login_payload)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data

def test_invalid_login(client: TestClient):
    payload = {
            "username": "invalid@invalid.com",
            "password": "invalid"
            }
    response = client.post("/auth/login", data=payload)
    response_data = response.json()

    assert response.status_code == 401