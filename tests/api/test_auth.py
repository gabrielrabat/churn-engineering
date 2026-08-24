from __future__ import annotations

import jwt
import pytest
from fastapi import HTTPException

from src.api.auth import authenticate_user, create_access_token, get_current_user
from src.api.core import ALGORITHM, DEMO_PASSWORD, DEMO_USER, SECRET_KEY


def test_authenticate_user_accepts_demo_credentials():
    assert authenticate_user(DEMO_USER, DEMO_PASSWORD) is True


def test_authenticate_user_rejects_wrong_password():
    assert authenticate_user(DEMO_USER, "wrong-password") is False


def test_authenticate_user_rejects_wrong_username():
    assert authenticate_user("someone-else", DEMO_PASSWORD) is False


def test_create_access_token_contains_username_and_is_decodable():
    token = create_access_token("gabriel")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "gabriel"
    assert "exp" in payload


def test_get_current_user_returns_username_from_valid_token():
    token = create_access_token("gabriel")

    current_user = get_current_user(token)

    assert current_user == {"username": "gabriel"}


def test_get_current_user_rejects_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("not-a-valid-jwt")

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_token_signed_with_wrong_key():
    bad_token = jwt.encode({"sub": "gabriel"}, "a-completely-different-wrong-secret-key", algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(bad_token)

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_token_without_subject():
    token_without_sub = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token_without_sub)

    assert exc_info.value.status_code == 401
