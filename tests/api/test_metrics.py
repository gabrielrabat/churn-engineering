from __future__ import annotations

from prometheus_client import Counter, Histogram

from src.api.metrics import (
    BATCH_PREDICTION_LATENCY,
    BATCH_PREDICTIONS_TOTAL,
    LOGIN_ATTEMPTS_TOTAL,
    PREDICTION_LATENCY,
    PREDICTIONS_TOTAL,
    RATE_LIMIT_EXCEEDED,
)


def test_predictions_total_is_a_counter_labeled_by_churn_and_user():
    assert isinstance(PREDICTIONS_TOTAL, Counter)
    PREDICTIONS_TOTAL.labels(churn="Yes", user="tester").inc()


def test_prediction_latency_is_a_histogram():
    assert isinstance(PREDICTION_LATENCY, Histogram)
    PREDICTION_LATENCY.observe(0.05)


def test_batch_predictions_total_is_labeled_by_user_and_batch_size():
    assert isinstance(BATCH_PREDICTIONS_TOTAL, Counter)
    BATCH_PREDICTIONS_TOTAL.labels(user="tester", batch_size="5").inc()


def test_batch_prediction_latency_is_a_histogram():
    assert isinstance(BATCH_PREDICTION_LATENCY, Histogram)
    BATCH_PREDICTION_LATENCY.observe(0.5)


def test_rate_limit_exceeded_is_labeled_by_endpoint_and_client_ip():
    assert isinstance(RATE_LIMIT_EXCEEDED, Counter)
    RATE_LIMIT_EXCEEDED.labels(endpoint="/predict", client_ip="127.0.0.1").inc()


def test_login_attempts_total_is_labeled_by_result():
    assert isinstance(LOGIN_ATTEMPTS_TOTAL, Counter)
    LOGIN_ATTEMPTS_TOTAL.labels(result="success").inc()
