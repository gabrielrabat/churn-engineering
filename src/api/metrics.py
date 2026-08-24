"""Metricas customizadas do Prometheus para a API de churn."""
from prometheus_client import Counter, Histogram

PREDICTIONS_TOTAL = Counter(
    "churn_predictions_total",
    "Total de predicoes individuais realizadas, por classe prevista",
    ["churn", "user"],
)

PREDICTION_LATENCY = Histogram(
    "churn_prediction_latency_seconds",
    "Latencia da predicao individual (segundos)",
)

BATCH_PREDICTIONS_TOTAL = Counter(
    "churn_batch_predictions_total",
    "Total de requisicoes de predicao em lote, por usuario e tamanho do lote",
    ["user", "batch_size"],
)

BATCH_PREDICTION_LATENCY = Histogram(
    "churn_batch_prediction_latency_seconds",
    "Latencia da predicao em lote (segundos)",
)

RATE_LIMIT_EXCEEDED = Counter(
    "churn_rate_limit_exceeded_total",
    "Total de requisicoes bloqueadas por rate limiting",
    ["endpoint", "client_ip"],
)

LOGIN_ATTEMPTS_TOTAL = Counter(
    "churn_login_attempts_total",
    "Total de tentativas de login, por resultado (sucesso/falha)",
    ["result"],
)
