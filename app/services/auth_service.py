from app.schemas.user import UserCreate
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import get_settings
import structlog

env_settings = get_settings()

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

log = structlog.get_logger()

def hash_password(password: str) -> str:
    return password_context.hash(password)

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    hashed_password = hash_password(user_data.password.get_secret_value())
    new_user = User(email=user_data.email, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    log.info("user_created", email=user_data.email)

    return new_user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    select_query = select(User).where(User.email == email)

    result = await db.execute(select_query)
    user = result.scalar_one_or_none()

    if not user or not password_context.verify(password, user.hashed_password):
        log.warning("authentication_failed", email=email)
        return None
    else:
        return user

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=env_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, env_settings.SECRET_KEY, algorithm=env_settings.ALGORITHM)
