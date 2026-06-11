import os
import pytest
from unittest.mock import patch

os.environ.setdefault("AUTH_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base
from app.main import app
from app.dependencies import get_db
from app.cache import get_cache
from fastapi.testclient import TestClient
import asyncio

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

    with patch("app.grpc.server.serve"):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()
    asyncio.run(drop_tables())
