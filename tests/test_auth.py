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