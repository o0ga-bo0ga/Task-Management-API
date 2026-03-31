from .database import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import get_settings
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select

env_settings = get_settings()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, env_settings.SECRET_KEY, algorithms=[env_settings.ALGORITHM])
        sub = payload.get("sub")

        if sub is None:
            raise HTTPException(status_code=401,
                                detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"}
                                )

        select_query = select(User).where(User.email == sub)
        user = db.execute(select_query).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401,
                                detail="Could not find user",
                                headers={"WWW-Authenticate": "Bearer"}
                                )
        else: 
            return user

    except JWTError:
        raise HTTPException(status_code=401, 
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"}
                            )