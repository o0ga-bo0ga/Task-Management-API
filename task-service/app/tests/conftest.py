import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base
from app.dependencies import get_db, get_current_user, TokenUser
from app.cache import get_cache
from app.main import app
from fastapi.testclient import TestClient
import asyncio
from unittest.mock import patch

TEST_USER = TokenUser(id=1, email="test@example.com")

class TestUserManager:
    def __init__(self):
        self.current = TEST_USER

    def set_user(self, id: int, email: str):
        self.current = TokenUser(id=id, email=email)

user_manager = TestUserManager()

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db" 

engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

class FakeRedis:
    def __init__(self):
        self._store = {}

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        self._store[key] = value

    async def delete(self, key):
        self._store.pop(key, None)

    async def incr(self, key):
        self._store[key] = self._store.get(key, 0) + 1
        return self._store[key]

    async def expire(self, key, seconds):
        pass

async def override_get_cache():
    yield FakeRedis()

async def override_get_current_user():
    return user_manager.current

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
def client():
    asyncio.run(create_tables())

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(drop_tables())

@pytest.fixture(autouse=True)
def mock_celery():
    with patch("app.tasks.notification_tasks.send_notification.delay") as mock:
        mock.return_value.id = "fake-job-id"
        yield mock

@pytest.fixture()
def auth_client(client):
    client.headers.update({"Authorization": "Bearer fake-token"})
    yield client

@pytest.fixture()
def test_user():
    return {"email": "prakhar@example.com", "password": "12345678"}

@pytest.fixture()
def user_switcher():
    return user_manager