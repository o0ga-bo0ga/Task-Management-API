from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import create_user
from app.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    try:
        user = create_user(db, user_data)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")