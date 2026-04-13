import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
TEST_DATABASE_URL = "sqlite:///./test.db" 
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread":False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def auth_client(client):

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

    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client

@pytest.fixture()
def test_user():
    return {"email": "prakhar@example.com", "password": "12345678"}