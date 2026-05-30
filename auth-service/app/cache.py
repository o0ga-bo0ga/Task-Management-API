from .config import get_settings
import redis.asyncio as redis
from typing import AsyncGenerator

env_settings = get_settings()

REDIS_URL = env_settings.REDIS_URL

pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

async def get_cache() -> AsyncGenerator[redis.Redis, None]:
    client = redis.Redis(connection_pool=pool)

    try:
        yield client
    finally:
        await client.aclose()