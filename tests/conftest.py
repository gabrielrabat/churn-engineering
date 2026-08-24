"""Fixtures compartilhadas entre os testes de src/."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.api.schemas import CustomerData
from src.preprocessing import CATEGORICAL_COLUMNS, clean_categorical_values

SAMPLE_CUSTOMER: dict = dict(CustomerData.model_config["json_schema_extra"]["example"])


@pytest.fixture
def sample_customer() -> dict:
    """Um registro de cliente valido, no formato aceito por `predict_churn`."""
    return dict(SAMPLE_CUSTOMER)


def build_feature_names(customers: list[dict]) -> list[str]:
    """Replica o encoding do preprocessing para descobrir as colunas resultantes.

    Usado para construir um `FakeModel.feature_names_in_` coerente com os
    clientes de teste, sem precisar enumerar manualmente todas as colunas
    dummy geradas pelo one-hot encoding.
    """
    df = pd.DataFrame(customers)
    cleaned = clean_categorical_values(df)
    encoded = pd.get_dummies(cleaned, columns=CATEGORICAL_COLUMNS, drop_first=True, dtype="int")
    return list(encoded.columns)


class FakeModel:
    """Stub de um pipeline sklearn (mesma interface usada por `predict_churn`)."""

    def __init__(
        self,
        feature_names_in_: list[str],
        predictions: list[int] | None = None,
        probabilities: list[list[float]] | None = None,
    ):
        self.feature_names_in_ = np.array(feature_names_in_)
        self._predictions = predictions
        self._probabilities = probabilities
        self.named_steps = {"clf": self}

    def predict(self, X) -> np.ndarray:
        n = len(X)
        if self._predictions is None:
            return np.zeros(n, dtype=int)
        preds = list(self._predictions)
        return np.array([preds[i % len(preds)] for i in range(n)])

    def predict_proba(self, X) -> np.ndarray:
        n = len(X)
        if self._probabilities is None:
            return np.tile([0.8, 0.2], (n, 1))
        probs = list(self._probabilities)
        return np.array([probs[i % len(probs)] for i in range(n)])


@pytest.fixture
def fake_model(sample_customer) -> FakeModel:
    feature_names = build_feature_names([sample_customer])
    return FakeModel(
        feature_names_in_=feature_names,
        predictions=[0],
        probabilities=[[0.8, 0.2]],
    )
