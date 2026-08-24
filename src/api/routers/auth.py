"""Rotas de autenticacao: /auth/login, /auth/me."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import authenticate_user, create_access_token, get_current_user
from src.api.core import RATE_LIMIT_LOGIN
from src.api.logging_config import logger
from src.api.metrics import LOGIN_ATTEMPTS_TOTAL
from src.api.rate_limit import limiter
from src.api.schemas import Token

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login", response_model=Token)
@limiter.limit(RATE_LIMIT_LOGIN)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica o usuario e retorna um JWT.

    **Rate Limit:** 10 requisicoes por minuto

    **Credenciais de demonstracao:** ver variaveis de ambiente `DEMO_USER` /
    `DEMO_PASSWORD` (nao usar este fluxo de senha em texto puro em producao real).
    """
    if not authenticate_user(form_data.username, form_data.password):
        LOGIN_ATTEMPTS_TOTAL.labels(result="failure").inc()
        logger.warning("login_failed", extra={"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha invalidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    LOGIN_ATTEMPTS_TOTAL.labels(result="success").inc()
    logger.info("login_succeeded", extra={"username": form_data.username})
    token = create_access_token(form_data.username)
    return Token(access_token=token)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """Retorna o usuario associado ao token enviado."""
    return current_user
