"""
Middleware de Logging e Trace ID

Roda antes e depois de cada requisicao para:
- Gerar um trace_id unico e propaga-lo nos logs e headers de resposta.
- Medir a latencia total da requisicao.
- Logar automaticamente toda requisicao, sem precisar instrumentar cada rota.
"""
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id

        start_time = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Nao loga /metrics para nao poluir os logs (Prometheus faz scrape a cada 15s).
        if request.url.path != "/metrics":
            logger.info(
                "request_completed",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                    "client_ip": request.client.host if request.client else None,
                },
            )

        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(round(latency_ms, 2))
        return response
