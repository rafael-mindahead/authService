from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    create_access_token,
    verify_password
    )
from app.models.user import User
from app.schemas.user import UserCreate

def register_user(
        db: Session,
        user_data: UserCreate
) -> User:

    email = str(user_data.email).lower().strip()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )
    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "email ja foi registrado"
        )

    user = User (
        name = user_data.name,
        email = email,
        password_hash = hash_password(
            user_data.password
        )
    )
    db.add(user)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "email ja foi registrado"
        )
    db.refresh(user)

    return user


def authenticate_user(
        db: Session,
        login_data: UserLogin
) -> str:
    email = str(login_data.email).lower().strip()

    user = db.scalar(
        select(User).where(User.email == email)
    )
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais invalidas"
        )
    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais invalidas"
        )
    if not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Usuario inativo"
        )

    access_token = create_access_token(
        subject = str(user.id)
    )

    return access_token