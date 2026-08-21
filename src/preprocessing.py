"""
Pre-processamento de dados de clientes para o modelo de churn.

Replica exatamente as transformacoes aplicadas em
notebooks/model_comparison.ipynb antes do treino do modelo campeao:

1. Colapsa categorias dependentes de outro servico
   ("No phone service" / "No internet service") em "No".
2. Aplica one-hot encoding (drop_first=True) nas colunas categoricas.
3. Realinha as colunas ao conjunto exato de features que o modelo
   viu em treino (`model.feature_names_in_`), preenchendo com 0
   qualquer coluna dummy ausente no batch atual.

O passo 3 e obrigatorio: `pandas.get_dummies` so cria uma coluna para
uma categoria se ela aparecer no batch recebido. Como a API pode
receber 1 unico cliente, sem o realinhamento o formato das features
mudaria a cada requisicao.
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd

CATEGORICAL_COLUMNS = [
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract",
    "paperless_billing",
    "payment_method",
]

NUMERIC_COLUMNS = ["tenure_months", "monthly_charges", "total_charges", "cltv"]

RAW_FEATURE_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS

# Colunas cujo valor "No internet service" e equivalente a "No"
# (o cliente nao tem internet, logo nao pode ter o servico dependente).
_NO_INTERNET_SERVICE_COLUMNS = [
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
]


def clean_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """Colapsa categorias redundantes ('No phone/internet service' -> 'No')."""
    df = df.copy()
    df["multiple_lines"] = df["multiple_lines"].replace("No phone service", "No")
    df[_NO_INTERNET_SERVICE_COLUMNS] = df[_NO_INTERNET_SERVICE_COLUMNS].replace(
        "No internet service", "No"
    )
    return df


def encode_features(df: pd.DataFrame, expected_columns: Iterable[str]) -> pd.DataFrame:
    """Limpa, aplica one-hot encoding e realinha ao schema do modelo treinado.

    Args:
        df: DataFrame com as colunas em RAW_FEATURE_COLUMNS (1 ou mais linhas).
        expected_columns: `model.feature_names_in_` do modelo campeao.

    Returns:
        DataFrame pronto para `model.predict` / `model.predict_proba`.
    """
    df = clean_categorical_values(df)
    encoded = pd.get_dummies(df, columns=CATEGORICAL_COLUMNS, drop_first=True, dtype="int")
    return encoded.reindex(columns=list(expected_columns), fill_value=0)
