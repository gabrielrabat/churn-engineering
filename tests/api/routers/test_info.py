from __future__ import annotations

from src.api.core import APP_ENV, APP_NAME, MODEL_VERSION


def test_root_returns_basic_api_info(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == APP_NAME
    assert body["versao"] == MODEL_VERSION
    assert body["ambiente"] == APP_ENV
    assert body["docs"] == "/docs"


def test_health_reports_ok_when_model_is_loaded(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["modelo_carregado"] is True


def test_health_reports_degraded_when_model_failed_to_load(client_model_unavailable):
    response = client_model_unavailable.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["modelo_carregado"] is False


def test_model_info_returns_metadata_when_loaded(client, fake_model):
    response = client.get("/model/info")

    assert response.status_code == 200
    body = response.json()
    assert body["modelo_carregado"] is True
    assert body["algoritmo"] == "FakeModel"
    assert body["features"] == list(fake_model.feature_names_in_)


def test_model_info_returns_not_loaded_when_model_unavailable(client_model_unavailable):
    response = client_model_unavailable.get("/model/info")

    assert response.status_code == 200
    body = response.json()
    assert body["modelo_carregado"] is False
    assert body["algoritmo"] is None
    assert body["features"] is None


def test_metrics_endpoint_returns_prometheus_text_format(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
