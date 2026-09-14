from sqlalchemy import select

from app.database.database import SessionLocal
from app.models.user import User, UserRole

def create_user_and_login(
    client,
    email="auth@email.com",
    password="Senha123!"
):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Auth User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    return login_response.json()


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@email.com",
            "password": "Senha123!"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@email.com"
    assert data["is_active"] is True
    assert data["is_verified"] is False

    assert "password" not in data
    assert "password_hash" not in data



def test_duplicate_email(client):
    user = {
        "name": "Test User",
        "email": "duplicate@email.com",
        "password": "Senha123!"
    }

    first_response = client.post(
        "/auth/register",
        json=user
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json=user
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "email ja foi registrado"
    }


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@email.com",
            "password": "Senha123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@email.com",
            "password": "Senha123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "wrong@email.com",
            "password": "Senha123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@email.com",
            "password": "SenhaErrada"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Credenciais invalidas"
    }

def test_me_without_token(client):
    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401



def test_me_with_valid_token(client):
    tokens = create_user_and_login(
        client,
        email="me@email.com"
    )

    access_token = tokens["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "me@email.com"
    assert data["name"] == "Auth User"
    assert data["is_active"] is True

def test_user_cannot_access_admin(client):
    tokens = create_user_and_login(
        client,
        email="normal@email.com"
    )

    response = client.get(
        "/auth/admin",
        headers={
            "Authorization": (
                f"Bearer {tokens['access_token']}"
            )
        }
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Permissao insuficiente"
    }


def test_admin_can_access_admin_route(client):
    client.post(
        "/auth/register",
        json={
            "name": "Admin User",
            "email": "admin@email.com",
            "password": "Senha123!"
        }
    )

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == "admin@email.com"
            )
        )

        assert user is not None

        user.role = UserRole.ADMIN

        db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@email.com",
            "password": "Senha123!"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()[
        "access_token"
    ]

    response = client.get(
        "/auth/admin",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"] == "admin@email.com"
    assert data["role"] == "ADMIN"


def test_refresh_token(client):
    tokens = create_user_and_login(
        client,
        email="refresh@email.com"
    )

    old_refresh_token = tokens["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    assert data["refresh_token"] != old_refresh_token

def test_refresh_token_cannot_be_reused(client):
    tokens = create_user_and_login(
        client,
        email="rotation@email.com"
    )

    old_refresh_token = tokens["refresh_token"]

    first_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert second_response.status_code == 401

def test_logout(client):
    tokens = create_user_and_login(
        client,
        email="logout@email.com"
    )

    refresh_token = tokens["refresh_token"]

    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 204


def test_logout_revokes_refresh_token(client):
    tokens = create_user_and_login(
        client,
        email="logout-revoke@email.com"
    )

    refresh_token = tokens["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 204

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401

def test_brute_force_protection(client):
    client.post(
        "/auth/register",
        json={
            "name": "Blocked User",
            "email": "blocked@email.com",
            "password": "Senha123!"
        }
    )

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": "blocked@email.com",
                "password": "SenhaErrada"
            }
        )

        assert response.status_code == 401

    blocked_response = client.post(
        "/auth/login",
        json={
            "email": "blocked@email.com",
            "password": "Senha123!"
        }
    )

    assert blocked_response.status_code == 429