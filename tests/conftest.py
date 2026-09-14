import os

os.environ["APP_ENV"] = "test"

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.redis_client import redis_client
from app.database.database import (
    Base,
    SessionLocal,
    engine
)
from app.main import app
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def setup_database():
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