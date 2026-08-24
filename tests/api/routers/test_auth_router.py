from __future__ import annotations

from src.api.core import DEMO_PASSWORD, DEMO_USER
from tests.api.conftest import login


def test_login_with_valid_credentials_returns_bearer_token(client):
    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_invalid_password_returns_401(client):
    response = login(client, password="wrong-password")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_with_invalid_username_returns_401(client):
    response = login(client, username="not-the-demo-user")

    assert response.status_code == 401


def test_me_without_token_is_rejected(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_is_rejected(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401


def test_me_with_valid_token_returns_username(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"username": DEMO_USER}
