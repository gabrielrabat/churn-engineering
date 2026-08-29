"""
API de Predicao de Churn - FastAPI bootstrap + routers

Carrega o modelo campeao (RandomForest, ver notebooks/model_comparison.ipynb)
uma unica vez na inicializacao e expoe endpoints de autenticacao, predicao
(individual e em lote), health check e metricas Prometheus.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.types import ExceptionHandler

from src.api.core import APP_NAME, CORS_ORIGINS, MODEL_PATH, MODEL_VERSION
from src.api.logging_config import logger
from src.api.middleware import LoggingMiddleware
from src.api.rate_limit import limiter, rate_limit_exceeded_handler
from src.api.routers import auth as auth_router
from src.api.routers import info as info_router
from src.api.routers import predict as predict_router
from src.model_loader import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.model = load_model(MODEL_PATH)
        app.state.modelo_ok = True
        logger.info(
            "model_loaded",
            extra={"model_path": MODEL_PATH, "model_version": MODEL_VERSION},
        )
    except FileNotFoundError as exc:
        app.state.model = None
        app.state.modelo_ok = False
        logger.error("model_load_failed", extra={"error": str(exc)})

    yield


app = FastAPI(
    title=APP_NAME,
    version=MODEL_VERSION,
    description=(
        "API REST para predicao de propensao a churn de clientes de "
        "telecomunicacoes, a partir de um modelo RandomForest treinado "
        "com Scikit-Learn."
    ),
    lifespan=lifespan,
)

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(ExceptionHandler, rate_limit_exceeded_handler))
app.add_middleware(SlowAPIMiddleware)

# --- Logging + trace_id ---
app.add_middleware(LoggingMiddleware)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(info_router.router)
app.include_router(auth_router.router)
app.include_router(predict_router.router)
