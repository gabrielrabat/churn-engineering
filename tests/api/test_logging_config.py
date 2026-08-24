from __future__ import annotations

import logging

from src.api.logging_config import CustomJsonFormatter, setup_logging


def test_setup_logging_returns_logger_named_api():
    logger = setup_logging()
    assert logger.name == "api"


def test_setup_logging_sets_level_from_argument():
    logger = setup_logging("WARNING")
    assert logger.level == logging.WARNING


def test_setup_logging_does_not_propagate_to_root():
    logger = setup_logging()
    assert logger.propagate is False


def test_setup_logging_attaches_a_single_stream_handler():
    logger = setup_logging()
    assert len(logger.handlers) == 1


def test_custom_json_formatter_adds_standard_fields():
    formatter = CustomJsonFormatter()
    record = logging.LogRecord(
        name="api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=None,
        exc_info=None,
    )

    log_record: dict = {}
    formatter.add_fields(log_record, record, {})

    assert log_record["level"] == "INFO"
    assert log_record["service"] == "api-churn"
    assert log_record["logger"] == "api"
    assert log_record["message"] == "hello"
    assert "timestamp" in log_record
