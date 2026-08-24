from __future__ import annotations

from src.api.core import BATCH_MAX_ITEMS, DEMO_USER
from tests.api.conftest import login
from tests.conftest import SAMPLE_CUSTOMER


def test_predict_requires_authentication(client):
    response = client.post("/predict", json=SAMPLE_CUSTOMER)

    assert response.status_code == 401


def test_predict_returns_prediction_for_authenticated_user(client, auth_headers):
    response = client.post("/predict", json=SAMPLE_CUSTOMER, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["sucesso"] is True
    assert body["churn"] == "No"
    assert body["probabilidade_churn"] == 0.2
    assert body["confianca"] == 0.8
    assert body["usuario"] == DEMO_USER
    assert body["tempo_ms"] >= 0


def test_predict_rejects_invalid_payload(client, auth_headers):
    invalid_customer = dict(SAMPLE_CUSTOMER, gender="Unknown")

    response = client.post("/predict", json=invalid_customer, headers=auth_headers)

    assert response.status_code == 422


def test_predict_returns_503_when_model_unavailable(client_model_unavailable):
    token = login(client_model_unavailable).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client_model_unavailable.post(
        "/predict", json=SAMPLE_CUSTOMER, headers=headers
    )

    assert response.status_code == 503


def test_predict_batch_requires_authentication(client):
    response = client.post("/predict/batch", json={"items": [SAMPLE_CUSTOMER]})

    assert response.status_code == 401


def test_predict_batch_returns_a_prediction_per_item(client, auth_headers):
    payload = {"items": [SAMPLE_CUSTOMER, SAMPLE_CUSTOMER]}

    response = client.post("/predict/batch", json=payload, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["indice"] for item in body["predicoes"]] == [0, 1]
    assert body["usuario"] == DEMO_USER


def test_predict_batch_rejects_empty_items(client, auth_headers):
    response = client.post("/predict/batch", json={"items": []}, headers=auth_headers)

    assert response.status_code == 422


def test_predict_batch_rejects_more_items_than_max(client, auth_headers):
    payload = {"items": [SAMPLE_CUSTOMER] * (BATCH_MAX_ITEMS + 1)}

    response = client.post("/predict/batch", json=payload, headers=auth_headers)

    assert response.status_code == 422
