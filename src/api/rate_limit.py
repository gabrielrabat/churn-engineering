"""
Rate Limiting com SlowAPI

Protege a API contra abuso, limitando quantidade de requisicoes por IP
em uma janela de tempo (ex.: 30 requisicoes por minuto).
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.core import RATE_LIMIT_DEFAULT
from src.api.logging_config import logger
from src.api.metrics import RATE_LIMIT_EXCEEDED


def get_client_identifier(request: Request) -> str:
    """Identifica o cliente pelo IP, respeitando X-Forwarded-For atras de proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=[RATE_LIMIT_DEFAULT],
    storage_uri="memory://",  # Em producao com multiplas instancias, usar Redis.
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handler customizado: retorna JSON amigavel, loga e incrementa metrica."""
    client_ip = get_client_identifier(request)
    endpoint = request.url.path

    logger.warning(
        "rate_limit_exceeded",
        extra={"client_ip": client_ip, "endpoint": endpoint, "limit": str(exc.detail)},
    )
    RATE_LIMIT_EXCEEDED.labels(endpoint=endpoint, client_ip=client_ip).inc()

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Muitas requisicoes. Limite: {exc.detail}",
            "retry_after_seconds": 60,
        },
        headers={"Retry-After": "60"},
    )
