from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import create_user
from app.dependencies import get_db
from app.services.auth_service import authenticate_user, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        user = await create_user(db, user_data)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    
@router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401,
                                detail="Could not authenticate user",
                                headers={"WWW-Authenticate": "Bearer"}
                                )
    
    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }