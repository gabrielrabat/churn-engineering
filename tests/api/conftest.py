"""Fixtures compartilhadas entre os testes de src/api."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api import main as main_module
from src.api.core import DEMO_PASSWORD, DEMO_USER
from src.api.rate_limit import limiter
from tests.conftest import SAMPLE_CUSTOMER, FakeModel, build_feature_names


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Evita que o rate limiting (estado global em memoria) vaze entre testes."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def fake_model() -> FakeModel:
    feature_names = build_feature_names([SAMPLE_CUSTOMER])
    return FakeModel(
        feature_names_in_=feature_names,
        predictions=[0, 1],
        probabilities=[[0.8, 0.2], [0.3, 0.7]],
    )


@pytest.fixture
def client(monkeypatch, fake_model) -> TestClient:
    """TestClient com o modelo (fake) carregado com sucesso na lifespan."""
    monkeypatch.setattr(main_module, "load_model", lambda path: fake_model)
    with TestClient(main_module.app) as test_client:
        yield test_client


@pytest.fixture
def client_model_unavailable(monkeypatch) -> TestClient:
    """TestClient simulando falha no carregamento do modelo na lifespan."""

    def _raise(path):
        raise FileNotFoundError(f"modelo nao encontrado em {path}")

    monkeypatch.setattr(main_module, "load_model", _raise)
    with TestClient(main_module.app) as test_client:
        yield test_client


def login(client: TestClient, username: str = DEMO_USER, password: str = DEMO_PASSWORD):
    return client.post("/auth/login", data={"username": username, "password": password})


@pytest.fixture
def auth_headers(client) -> dict:
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
