from .database import SessionLocal
from fastapi import Depends
from app.config import get_settings

env_settings = get_settings()

async def get_db():
    async with SessionLocal() as db:
        yield db