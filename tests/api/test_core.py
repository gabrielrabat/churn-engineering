from __future__ import annotations

import importlib

from src.api import core


def _reload_with_env_change(monkeypatch, set_env: dict | None = None, del_env: list | None = None):
    """Aplica mudancas de env, recarrega `core` e devolve (modulo_recarregado, callback_de_restauracao)."""
    for key, value in (set_env or {}).items():
        monkeypatch.setenv(key, value)
    for key in del_env or []:
        monkeypatch.delenv(key, raising=False)
    reloaded = importlib.reload(core)

    def restore():
        monkeypatch.undo()
        importlib.reload(core)

    return reloaded, restore


def test_default_demo_credentials_when_env_not_set(monkeypatch):
    reloaded, restore = _reload_with_env_change(
        monkeypatch, del_env=["DEMO_USER", "DEMO_PASSWORD"]
    )
    try:
        assert reloaded.DEMO_USER == "admin"
        assert reloaded.DEMO_PASSWORD == "secret123"
    finally:
        restore()


def test_cors_origins_splits_comma_separated_env_var(monkeypatch):
    reloaded, restore = _reload_with_env_change(
        monkeypatch, set_env={"CORS_ORIGINS": "https://a.com, https://b.com"}
    )
    try:
        assert reloaded.CORS_ORIGINS == ["https://a.com", "https://b.com"]
    finally:
        restore()


def test_metrics_enabled_is_boolean_from_env(monkeypatch):
    reloaded, restore = _reload_with_env_change(monkeypatch, set_env={"METRICS_ENABLED": "false"})
    try:
        assert reloaded.METRICS_ENABLED is False
    finally:
        restore()


def test_batch_max_items_defaults_to_100():
    assert core.BATCH_MAX_ITEMS == 100
