from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from app.cache import pool

async def rate_limit_login(request: Request):
    client = redis.Redis(connection_pool=pool)

    ip = request.client.host
    key = f"rate_limit:login:{ip}"

    count = await client.incr(key)

    if count == 1:
        await client.expire(key, 60)

    if count > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in a minute."
        )