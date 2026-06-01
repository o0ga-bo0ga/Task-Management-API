from fastapi.testclient import TestClient

def test_valid_registration(client: TestClient):
    payload = {"email": "test@example.com", "password": "12345678"}
    response = client.post("/auth/register", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data

def test_duplicate_registration(client: TestClient):
    payload = {"email": "dup@example.com", "password": "12345678"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_successful_login(client: TestClient):
    client.post("/auth/register", json={"email": "login@example.com", "password": "12345678"})
    response = client.post("/auth/login", data={"username": "login@example.com", "password": "12345678"})
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient):
    client.post("/auth/register", json={"email": "wrongpass@example.com", "password": "12345678"})
    response = client.post("/auth/login", data={"username": "wrongpass@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert "Could not authenticate user" in response.json()["detail"]

def test_login_unregistered_user(client: TestClient):
    response = client.post("/auth/login", data={"username": "nobody@example.com", "password": "12345678"})

    assert response.status_code == 401
    assert "Could not authenticate user" in response.json()["detail"]

def test_registration_missing_email(client: TestClient):
    response = client.post("/auth/register", json={"password": "12345678"})

    assert response.status_code == 422

def test_registration_missing_password(client: TestClient):
    response = client.post("/auth/register", json={"email": "test@example.com"})

    assert response.status_code == 422

def test_registration_invalid_email(client: TestClient):
    payload = {"email": "not-an-email", "password": "12345678"}
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422
