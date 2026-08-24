"""Modelos Pydantic de request/response da API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from src.api.core import BATCH_MAX_ITEMS

YesNo = Literal["Yes", "No"]
InternetDependentService = Literal["Yes", "No", "No internet service"]


class CustomerData(BaseModel):
    """Dados brutos de um cliente, no mesmo formato do dataset de treino."""

    gender: Literal["Female", "Male"]
    senior_citizen: YesNo
    partner: YesNo
    dependents: YesNo
    tenure_months: int = Field(ge=0, le=100, description="Meses de permanencia do cliente")
    phone_service: YesNo
    multiple_lines: Literal["Yes", "No", "No phone service"]
    internet_service: Literal["DSL", "Fiber optic", "No"]
    online_security: InternetDependentService
    online_backup: InternetDependentService
    device_protection: InternetDependentService
    tech_support: InternetDependentService
    streaming_tv: InternetDependentService
    streaming_movies: InternetDependentService
    contract: Literal["Month-to-month", "One year", "Two year"]
    paperless_billing: YesNo
    payment_method: Literal[
        "Bank transfer (automatic)",
        "Credit card (automatic)",
        "Electronic check",
        "Mailed check",
    ]
    monthly_charges: float = Field(gt=0, description="Cobranca mensal em USD")
    total_charges: float = Field(ge=0, description="Total cobrado ate o momento em USD")
    cltv: float = Field(ge=0, description="Customer Lifetime Value estimado")

    model_config = {
        "json_schema_extra": {
            "example": {
                "gender": "Female",
                "senior_citizen": "No",
                "partner": "Yes",
                "dependents": "No",
                "tenure_months": 1,
                "phone_service": "No",
                "multiple_lines": "No phone service",
                "internet_service": "DSL",
                "online_security": "No",
                "online_backup": "Yes",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "No",
                "streaming_movies": "No",
                "contract": "Month-to-month",
                "paperless_billing": "Yes",
                "payment_method": "Electronic check",
                "monthly_charges": 29.85,
                "total_charges": 29.85,
                "cltv": 3239,
            }
        }
    }


class PredictResponse(BaseModel):
    sucesso: bool
    churn: Literal["Yes", "No"]
    probabilidade_churn: float
    confianca: float
    tempo_ms: float
    usuario: str


class BatchPredictRequest(BaseModel):
    items: list[CustomerData] = Field(min_length=1, max_length=BATCH_MAX_ITEMS)


class BatchPredictItem(BaseModel):
    indice: int
    churn: Literal["Yes", "No"]
    probabilidade_churn: float
    confianca: float


class BatchPredictResponse(BaseModel):
    sucesso: bool
    total: int
    tempo_total_ms: float
    predicoes: list[BatchPredictItem]
    usuario: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    modelo_carregado: bool
    ambiente: str


class ModelInfoResponse(BaseModel):
    modelo_carregado: bool
    versao: str
    algoritmo: str | None = None
    features: list[str] | None = None
