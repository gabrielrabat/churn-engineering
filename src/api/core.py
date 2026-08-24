"""Configuracoes globais da aplicacao, lidas de variaveis de ambiente.

Nenhum valor sensivel fica hardcoded fora de defaults de desenvolvimento;
em producao (Render/Docker), todas essas variaveis devem ser sobrescritas.
Veja `.env.example` para a lista completa.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# --- Aplicacao ---
APP_NAME = "API de Predicao de Churn"
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Modelo ---
MODEL_PATH = os.getenv("MODEL_PATH", str(PROJECT_ROOT / "models" / "champion_model.joblib"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0")

# --- Seguranca / JWT ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production-32bytes")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# --- Usuario de demonstracao ---
# Em producao real isso viria de um banco de dados com senhas hasheadas.
DEMO_USER = os.getenv("DEMO_USER", "admin")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "secret123")

# --- Rate limiting (formato aceito pelo slowapi: "N/second|minute|hour|day") ---
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
RATE_LIMIT_PREDICT = os.getenv("RATE_LIMIT_PREDICT", "30/minute")
RATE_LIMIT_BATCH = os.getenv("RATE_LIMIT_BATCH", "10/minute")
RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "10/minute")

# --- Predicao em lote ---
BATCH_MAX_ITEMS = int(os.getenv("BATCH_MAX_ITEMS", "100"))

# --- Metricas / CORS ---
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
