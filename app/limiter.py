from fastapi import Request, HTTPException, status, Depends
import redis.asyncio as Redis
from app.cache import get_cache

async def rate_limit_login(request: Request,
                           client: Redis = Depends(get_cache)):

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