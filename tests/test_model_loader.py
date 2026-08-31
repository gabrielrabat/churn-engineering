from __future__ import annotations

import re
from pathlib import Path

import joblib
import pytest

from src.model_loader import load_model


def test_load_model_raises_file_not_found_for_missing_path(tmp_path):
    missing_path = tmp_path / "does_not_exist.joblib"

    with pytest.raises(FileNotFoundError, match=re.escape(str(missing_path))):
        load_model(missing_path)


def test_load_model_returns_the_object_dumped_on_disk(tmp_path):
    model_path = tmp_path / "fake_model.joblib"
    original = {"kind": "fake-pipeline", "version": 1}
    joblib.dump(original, model_path)

    loaded = load_model(model_path)

    assert loaded == original


def test_load_model_accepts_str_path(tmp_path):
    model_path = tmp_path / "fake_model.joblib"
    joblib.dump("payload", model_path)

    loaded = load_model(str(model_path))

    assert loaded == "payload"
