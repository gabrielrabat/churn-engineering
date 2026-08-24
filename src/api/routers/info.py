"""Rotas de informacao e observabilidade: /, /health, /model/info, /metrics."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.core import APP_ENV, APP_NAME, METRICS_ENABLED, MODEL_VERSION
from src.api.schemas import HealthResponse, ModelInfoResponse

router = APIRouter(tags=["Info"])


@router.get("/")
def root():
    """Informacoes basicas da API."""
    return {
        "nome": APP_NAME,
        "versao": MODEL_VERSION,
        "ambiente": APP_ENV,
        "docs": "/docs",
    }


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    """Verifica se a API esta no ar e se o modelo foi carregado com sucesso."""
    modelo_carregado = bool(getattr(request.app.state, "modelo_ok", False))
    return HealthResponse(
        status="ok" if modelo_carregado else "degraded",
        modelo_carregado=modelo_carregado,
        ambiente=APP_ENV,
    )


@router.get("/model/info", response_model=ModelInfoResponse)
def model_info(request: Request):
    """Retorna metadados do modelo de churn atualmente carregado."""
    model = getattr(request.app.state, "model", None)
    modelo_carregado = bool(getattr(request.app.state, "modelo_ok", False))

    if not modelo_carregado or model is None:
        return ModelInfoResponse(modelo_carregado=False, versao=MODEL_VERSION)

    classifier = model.named_steps.get("clf") if hasattr(model, "named_steps") else model
    return ModelInfoResponse(
        modelo_carregado=True,
        versao=MODEL_VERSION,
        algoritmo=type(classifier).__name__,
        features=list(model.feature_names_in_),
    )


@router.get("/metrics")
def metrics():
    """Expoe metricas no formato Prometheus."""
    if not METRICS_ENABLED:
        return Response(status_code=404)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
