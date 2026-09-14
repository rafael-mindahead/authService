from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import (
    get_current_user,
    require_role
)
from app.models.user import User, UserRole
from app.schemas.user import RefreshTokenRequest
from app.services.auth_service import refresh_tokens

from app.database.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    logout_user,
    refresh_tokens,
    request_password_reset,
    reset_password
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
    access_token, refresh_token = authenticate_user(
        db=db,
        login_data = login_data
    )

    return TokenResponse(
        access_token = access_token,
        refresh_token=refresh_token,
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

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh(
    token_data: RefreshTokenRequest
):

    access_token, refresh_token = refresh_tokens(
        token_data.refresh_token
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )



@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
def logout(
    token_data: RefreshTokenRequest
):
    logout_user(
        token_data.refresh_token
    )

    return None

@router.get("/admin")
def admin_area(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    )
):
    return {
        "message": "Bem-vindo a area administrativa",
        "user": current_user.email,
        "role": current_user.role
    }

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    reset_token = request_password_reset(
        db,
        str(data.email)
    )

    if reset_token:
        print(
            f"[DEV] Password reset token: {reset_token}"
        )

    return {
        "message": (
            "Se o email estiver cadastrado, "
            "enviaremos instrucoes para redefinir a senha."
        )
    }

@router.post("/reset-password")
def reset_user_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    reset_password(
        db=db,
        token=data.token,
        new_password=data.new_password
    )

    return {
        "message": "Senha redefinida com sucesso"
    }