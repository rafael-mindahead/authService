import os

os.environ["APP_ENV"] = "test"

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.redis_client import redis_client
from app.core.config import settings
from urllib.parse import urlparse
from app.database.database import (
    Base,
    SessionLocal,
    engine
)
from app.main import app
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # These tests drop/recreate tables; never let them run on non-test databases.
    database_name = urlparse(settings.DATABASE_URL).path.lstrip("/")
    redis_database = urlparse(settings.REDIS_URL).path.lstrip("/")
    if os.environ.get("APP_ENV") != "test" or not database_name.endswith("_test") or redis_database != "1":
        raise RuntimeError("Refusing destructive tests outside the isolated _test PostgreSQL database and Redis DB 1")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    redis_client.flushdb()

    with SessionLocal() as db:
        db.execute(delete(User))
        db.commit()

    yield


@pytest.fixture
def client():
    return TestClient(app)