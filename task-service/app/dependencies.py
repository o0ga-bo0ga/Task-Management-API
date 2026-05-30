from .database import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import get_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass

env_settings = get_settings()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@dataclass
class TokenUser:
    id: int
    email: str

async def get_db():
    async with SessionLocal() as db:
        yield db

async def get_current_user(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, env_settings.SECRET_KEY, algorithms=[env_settings.ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if email is None or user_id is None:
            raise HTTPException(status_code=401,
                                detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})

        return TokenUser(id=user_id, email=email)

    except JWTError:
        raise HTTPException(status_code=401,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})