"""
Autenticacao via JWT (OAuth2 Password Flow simplificado)

Usuario unico de demonstracao (DEMO_USER/DEMO_PASSWORD), suficiente para o
escopo do Tech Challenge. Em producao real, troque por um banco de usuarios
com senhas hasheadas (ex.: passlib + bcrypt) em vez de comparacao direta.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.api.core import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    DEMO_PASSWORD,
    DEMO_USER,
    SECRET_KEY,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def authenticate_user(username: str, password: str) -> bool:
    """Valida usuario/senha contra as credenciais de demonstracao."""
    return username == DEMO_USER and password == DEMO_PASSWORD


def create_access_token(username: str) -> str:
    """Gera um JWT assinado, valido por ACCESS_TOKEN_EXPIRE_MINUTES minutos."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency do FastAPI: decodifica o Bearer token e retorna o usuario atual."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc
    return {"username": username}
