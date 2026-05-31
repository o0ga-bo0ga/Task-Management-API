from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

env_settings = get_settings()

sync_engine = create_engine(env_settings.DATABASE_URL.replace("+asyncpg", ""))
engine = create_async_engine(env_settings.DATABASE_URL)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

Base = declarative_base()