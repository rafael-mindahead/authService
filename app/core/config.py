import os
from pydantic_settings import BaseSettings, SettingsConfigDict
ENV_FILE = (
    ".env.test"
    if os.getenv("APP_ENV") == "test"
    else ".env"
)
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_BLOCK_SECONDS: int = 900

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra = "ignore"
    )



settings = Settings()