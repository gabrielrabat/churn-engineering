"""Rotas de predicao: /predict e /predict/batch."""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import get_current_user
from src.api.core import RATE_LIMIT_BATCH, RATE_LIMIT_PREDICT
from src.api.logging_config import logger
from src.api.metrics import (
    BATCH_PREDICTION_LATENCY,
    BATCH_PREDICTIONS_TOTAL,
    PREDICTION_LATENCY,
    PREDICTIONS_TOTAL,
)
from src.api.rate_limit import limiter
from src.api.schemas import (
    BatchPredictItem,
    BatchPredictRequest,
    BatchPredictResponse,
    CustomerData,
    PredictResponse,
)
from src.predict import predict_churn

router = APIRouter(tags=["Predicao"])


def _get_model(request: Request):
    if not getattr(request.app.state, "modelo_ok", False):
        raise HTTPException(status_code=503, detail="Modelo nao disponivel")
    return request.app.state.model


@router.post("/predict", response_model=PredictResponse)
@limiter.limit(RATE_LIMIT_PREDICT)
def predict(
    request: Request,
    payload: CustomerData,
    current_user: dict = Depends(get_current_user),
):
    """
    Faz a predicao de churn para um unico cliente.

    **Rate Limit:** 30 requisicoes por minuto

    **Requer autenticacao:** Inclua o header `Authorization: Bearer <token>`
    """
    model = _get_model(request)
    trace_id = getattr(request.state, "trace_id", "N/A")
    start = time.perf_counter()

    resultado = predict_churn(model, [payload.model_dump()])[0]

    latency = time.perf_counter() - start
    PREDICTIONS_TOTAL.labels(churn=resultado["churn"], user=current_user["username"]).inc()
    PREDICTION_LATENCY.observe(latency)

    logger.info(
        "prediction_completed",
        extra={
            "trace_id": trace_id,
            "user": current_user["username"],
            "churn": resultado["churn"],
            "latency_ms": round(latency * 1000, 2),
        },
    )

    return PredictResponse(
        sucesso=True,
        churn=resultado["churn"],
        probabilidade_churn=resultado["probabilidade_churn"],
        confianca=resultado["confianca"],
        tempo_ms=round(latency * 1000, 2),
        usuario=current_user["username"],
    )


@router.post("/predict/batch", response_model=BatchPredictResponse)
@limiter.limit(RATE_LIMIT_BATCH)
def predict_batch(
    request: Request,
    payload: BatchPredictRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Faz a predicao de churn para multiplos clientes de uma vez.

    **Rate Limit:** 10 requisicoes por minuto

    **Maximo:** ver `BATCH_MAX_ITEMS` (padrao: 100 clientes por requisicao)

    **Requer autenticacao:** Inclua o header `Authorization: Bearer <token>`
    """
    model = _get_model(request)
    trace_id = getattr(request.state, "trace_id", "N/A")
    start = time.perf_counter()

    customers = [item.model_dump() for item in payload.items]
    resultados = predict_churn(model, customers)

    predicoes = [
        BatchPredictItem(
            indice=i,
            churn=resultado["churn"],
            probabilidade_churn=resultado["probabilidade_churn"],
            confianca=resultado["confianca"],
        )
        for i, resultado in enumerate(resultados)
    ]

    for resultado in resultados:
        PREDICTIONS_TOTAL.labels(churn=resultado["churn"], user=current_user["username"]).inc()

    latency = time.perf_counter() - start
    batch_size = len(payload.items)

    BATCH_PREDICTIONS_TOTAL.labels(
        user=current_user["username"], batch_size=str(batch_size)
    ).inc()
    BATCH_PREDICTION_LATENCY.observe(latency)

    logger.info(
        "batch_prediction_completed",
        extra={
            "trace_id": trace_id,
            "user": current_user["username"],
            "batch_size": batch_size,
            "latency_ms": round(latency * 1000, 2),
            "avg_latency_per_item_ms": round((latency * 1000) / batch_size, 2),
        },
    )

    return BatchPredictResponse(
        sucesso=True,
        total=batch_size,
        tempo_total_ms=round(latency * 1000, 2),
        predicoes=predicoes,
        usuario=current_user["username"],
    )
