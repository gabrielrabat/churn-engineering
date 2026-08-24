from __future__ import annotations

import pandas as pd
import pytest

from src.preprocessing import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    RAW_FEATURE_COLUMNS,
    clean_categorical_values,
    encode_features,
)


def test_raw_feature_columns_is_categorical_plus_numeric():
    assert RAW_FEATURE_COLUMNS == CATEGORICAL_COLUMNS + NUMERIC_COLUMNS


def test_clean_categorical_values_collapses_no_phone_service():
    df = pd.DataFrame(
        {
            "multiple_lines": ["No phone service", "Yes", "No"],
            "online_security": ["No", "No", "No"],
            "online_backup": ["No", "No", "No"],
            "device_protection": ["No", "No", "No"],
            "tech_support": ["No", "No", "No"],
            "streaming_tv": ["No", "No", "No"],
            "streaming_movies": ["No", "No", "No"],
        }
    )
    cleaned = clean_categorical_values(df)
    assert cleaned["multiple_lines"].tolist() == ["No", "Yes", "No"]


def test_clean_categorical_values_collapses_no_internet_service():
    df = pd.DataFrame(
        {
            "multiple_lines": ["No", "No", "No"],
            "online_security": ["No internet service", "Yes", "No"],
            "online_backup": ["No internet service", "No", "Yes"],
            "device_protection": ["No internet service", "No", "No"],
            "tech_support": ["No internet service", "No", "No"],
            "streaming_tv": ["No internet service", "No", "No"],
            "streaming_movies": ["No internet service", "No", "No"],
        }
    )
    cleaned = clean_categorical_values(df)
    for column in [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]:
        assert cleaned[column].iloc[0] == "No"


def test_clean_categorical_values_does_not_mutate_input():
    df = pd.DataFrame(
        {
            "multiple_lines": ["No phone service"],
            "online_security": ["No internet service"],
            "online_backup": ["No internet service"],
            "device_protection": ["No internet service"],
            "tech_support": ["No internet service"],
            "streaming_tv": ["No internet service"],
            "streaming_movies": ["No internet service"],
        }
    )
    original = df.copy()
    clean_categorical_values(df)
    pd.testing.assert_frame_equal(df, original)


def test_encode_features_fills_missing_dummy_columns_with_zero(sample_customer):
    all_female = pd.DataFrame([sample_customer, sample_customer])  # gender = "Female" only
    expected_columns = ["gender_Male", "tenure_months"]

    encoded = encode_features(all_female, expected_columns)

    assert list(encoded.columns) == expected_columns
    assert (encoded["gender_Male"] == 0).all()
    assert encoded["tenure_months"].tolist() == [
        sample_customer["tenure_months"],
        sample_customer["tenure_months"],
    ]


def test_encode_features_creates_dummy_for_present_category(sample_customer):
    male_customer = dict(sample_customer, gender="Male")
    raw = pd.DataFrame([sample_customer, male_customer])

    encoded = encode_features(raw, expected_columns=["gender_Male"])

    assert encoded["gender_Male"].tolist() == [0, 1]


def test_encode_features_treats_no_phone_service_as_equivalent_to_no(sample_customer):
    with_no_phone_service = dict(sample_customer, phone_service="No", multiple_lines="No phone service")
    with_plain_no = dict(sample_customer, phone_service="No", multiple_lines="No")
    raw = pd.DataFrame([with_no_phone_service, with_plain_no])

    encoded = encode_features(raw, expected_columns=["multiple_lines_Yes"])

    assert encoded["multiple_lines_Yes"].tolist() == [0, 0]


def test_encode_features_orders_columns_per_expected_columns(sample_customer):
    raw = pd.DataFrame([sample_customer])
    expected_columns = ["cltv", "tenure_months", "gender_Male"]

    encoded = encode_features(raw, expected_columns)

    assert list(encoded.columns) == expected_columns


def test_encode_features_drops_columns_not_in_expected_columns(sample_customer):
    raw = pd.DataFrame([sample_customer])

    encoded = encode_features(raw, expected_columns=["tenure_months"])

    assert list(encoded.columns) == ["tenure_months"]


@pytest.mark.parametrize("num_rows", [1, 3])
def test_encode_features_preserves_row_count(sample_customer, num_rows):
    raw = pd.DataFrame([sample_customer] * num_rows)

    encoded = encode_features(raw, expected_columns=["tenure_months"])

    assert len(encoded) == num_rows
