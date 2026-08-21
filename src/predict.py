"""Inferencia de churn a partir do modelo campeao ja carregado."""
from __future__ import annotations

from typing import Any

import pandas as pd

from src.preprocessing import encode_features

CHURN_LABELS = {0: "No", 1: "Yes"}


def customers_to_dataframe(customers: list[dict]) -> pd.DataFrame:
    """Converte uma lista de registros de clientes (dicts) em DataFrame."""
    return pd.DataFrame(customers)


def predict_churn(model: Any, customers: list[dict]) -> list[dict]:
    """Roda o pipeline completo de pre-processamento + predicao.

    Args:
        model: pipeline sklearn carregado via `src.model_loader.load_model`.
        customers: lista de dicts com as chaves em
            `src.preprocessing.RAW_FEATURE_COLUMNS`.

    Returns:
        Uma lista (na mesma ordem de `customers`) com:
            - churn: "Yes" | "No"
            - probabilidade_churn: probabilidade da classe positiva (Yes)
            - confianca: probabilidade da classe prevista
    """
    raw_df = customers_to_dataframe(customers)
    features = encode_features(raw_df, model.feature_names_in_)

    pred_indices = model.predict(features)
    probabilities = model.predict_proba(features)

    results = []
    for pred_idx, probs in zip(pred_indices, probabilities):
        results.append(
            {
                "churn": CHURN_LABELS[int(pred_idx)],
                "probabilidade_churn": round(float(probs[1]), 4),
                "confianca": round(float(max(probs)), 4),
            }
        )
    return results
