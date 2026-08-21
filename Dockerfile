# =============================================================================
# Dockerfile - API de Predicao de Churn
# =============================================================================
# Imagem enxuta: usa requirements-api.txt (so o necessario para servir o
# modelo), nao o requirements.txt completo de desenvolvimento (Jupyter,
# scikit-learn, matplotlib etc.).
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/ ./src/
COPY models/champion_model.joblib ./models/champion_model.joblib

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
