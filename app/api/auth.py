from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.database.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse
)
from app.services.auth_service import (
    register_user,
    authenticate_user
    )


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return register_user(
        db=db,
        user_data=user_data
    )


@router.post(
    "/login",
    response_model = TokenResponse
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    access_token = authenticate_user(
        db=db,
        login_data = login_data
    )

    return TokenResponse(
        access_token = access_token,
        token_type = "bearer"
    )


@router.get(
    "/me",
    response_model = UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user