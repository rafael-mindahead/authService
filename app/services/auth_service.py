from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.security import (
    hash_password,
    create_access_token,
    verify_password,
    create_refresh_token,
    hash_refresh_token
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


def get_login_attempts(email: str) -> int:
    key = f"login_attempts:{email}"

    attempts = redis_client.get(key)

    if attempts is None:
        return 0

    return int(attempts)


def register_failed_login(email: str) -> None:
    key = f"login_attempts:{email}"

    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(
            key,
            settings.LOGIN_BLOCK_SECONDS
        )


def clear_login_attempts(email: str) -> None:
    redis_client.delete(
        f"login_attempts:{email}"
    )


def authenticate_user(
        db: Session,
        login_data: UserLogin
) -> str:
    email = str(login_data.email).lower().strip()

    attempts = get_login_attempts(email)

    
    if attempts >= settings.LOGIN_MAX_ATTEMPTS:
        ttl = redis_client.ttl(
            f"login_attempts:{email}"
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {ttl} segundos."
        )

    user = db.scalar(
        select(User).where(User.email == email)
    )
    if not user:
        register_failed_login(email)

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais invalidas"
        )
    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        register_failed_login(email)
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais invalidas"
        )
    if not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Usuario inativo"
        )
    
    clear_login_attempts(email)

    access_token = create_access_token(
    subject=str(user.id)
    )

    refresh_token = create_refresh_token()

    refresh_token_hash = hash_refresh_token(
        refresh_token
    )

    redis_client.setex(
        f"refresh:{refresh_token_hash}",
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    str(user.id)
    )
    return access_token, refresh_token


def refresh_tokens(
    refresh_token: str
) -> tuple[str, str]:

    token_hash = hash_refresh_token(
        refresh_token
    )

    redis_key = f"refresh:{token_hash}"

    user_id = redis_client.get(
        redis_key
    )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido ou expirado"
        )

    # Remove o token antigo
    redis_client.delete(
        redis_key
    )

    new_access_token = create_access_token(
        subject=user_id
    )

    new_refresh_token = create_refresh_token()

    new_refresh_hash = hash_refresh_token(
        new_refresh_token
    )

    redis_client.setex(
        f"refresh:{new_refresh_hash}",
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        user_id
    )

    return (
        new_access_token,
        new_refresh_token
    )


def logout_user(
    refresh_token: str
) -> None:

    token_hash = hash_refresh_token(
        refresh_token
    )

    redis_key = f"refresh:{token_hash}"

    deleted = redis_client.delete(
        redis_key
    )

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao invalida ou ja encerrada"
        )