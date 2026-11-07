from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)

def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user :
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    user = User(
        name=user_data.name,
        email= str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login")
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)):

    user = (
        db.query(User)
        .filter(User.email == str(credentials.email))
        .first()
    )

    if user is None or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)

    return {
        "access_token" : access_token,
        "token_type": "bearer",
    }

