from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.api.schemas import BatchPredictRequest, CustomerData
from src.api.core import BATCH_MAX_ITEMS


def test_customer_data_accepts_the_documented_example(sample_customer):
    customer = CustomerData(**sample_customer)
    assert customer.gender == "Female"


def test_customer_data_rejects_invalid_literal_value(sample_customer):
    invalid = dict(sample_customer, gender="Other")

    with pytest.raises(ValidationError):
        CustomerData(**invalid)


def test_customer_data_rejects_negative_tenure_months(sample_customer):
    invalid = dict(sample_customer, tenure_months=-1)

    with pytest.raises(ValidationError):
        CustomerData(**invalid)


def test_customer_data_rejects_tenure_months_above_100(sample_customer):
    invalid = dict(sample_customer, tenure_months=101)

    with pytest.raises(ValidationError):
        CustomerData(**invalid)


def test_customer_data_rejects_non_positive_monthly_charges(sample_customer):
    invalid = dict(sample_customer, monthly_charges=0)

    with pytest.raises(ValidationError):
        CustomerData(**invalid)


def test_batch_predict_request_rejects_empty_items():
    with pytest.raises(ValidationError):
        BatchPredictRequest(items=[])


def test_batch_predict_request_rejects_more_than_max_items(sample_customer):
    items = [sample_customer] * (BATCH_MAX_ITEMS + 1)

    with pytest.raises(ValidationError):
        BatchPredictRequest(items=items)


def test_batch_predict_request_accepts_items_up_to_max(sample_customer):
    items = [sample_customer] * BATCH_MAX_ITEMS

    request = BatchPredictRequest(items=items)

    assert len(request.items) == BATCH_MAX_ITEMS
