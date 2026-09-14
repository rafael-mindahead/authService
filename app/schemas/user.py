from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: UserRole
    model_config = ConfigDict(
        from_attributes=True
    )



class UserLogin(BaseModel):
    email: EmailStr
    password: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=8,
        max_length=128
    )

