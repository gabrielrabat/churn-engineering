"""
Configuracao de Logs Estruturados (JSON)

Logs estruturados facilitam filtragem por campo (user, endpoint, status) e
correlacao de eventos via trace_id em ferramentas como CloudWatch/Kibana.
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone

from pythonjsonlogger import json

from src.api.core import LOG_LEVEL


class CustomJsonFormatter(json.JsonFormatter):
    """Adiciona timestamp, level, service e logger a cada registro de log."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["service"] = "api-churn"
        log_record["logger"] = record.name
        if not log_record.get("message"):
            log_record["message"] = record.getMessage()


def setup_logging(level: str = LOG_LEVEL) -> logging.Logger:
    """Cria (ou reconfigura) o logger `api` para emitir JSON em stdout."""
    logger = logging.getLogger("api")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s"))

    logger.handlers = []
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logging()
