"""Carregamento do modelo campeao (RandomForest) treinado em model_comparison.ipynb."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "champion_model.joblib"


def load_model(model_path: str | Path = DEFAULT_MODEL_PATH) -> Any:
    """Carrega o pipeline sklearn (preprocess + classificador) salvo em disco.

    Raises:
        FileNotFoundError: se o arquivo do modelo nao existir no caminho informado.
    """
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Modelo nao encontrado em: {path}")
    return joblib.load(path)
