from app.schemas.user import UserCreate
from app.models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return password_context.hash(password)

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = hash_password(user_data.password.get_secret_value())
    new_user = User(email=user_data.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
