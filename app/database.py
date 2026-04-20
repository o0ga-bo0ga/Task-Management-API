from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import get_settings

env_settings = get_settings()

engine = create_async_engine(env_settings.DATABASE_URL)

SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)
Base = declarative_base()