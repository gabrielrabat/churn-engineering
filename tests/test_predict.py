from __future__ import annotations

import pandas as pd
import pytest

from src.predict import CHURN_LABELS, customers_to_dataframe, predict_churn
from tests.conftest import FakeModel, build_feature_names


def test_churn_labels_mapping():
    assert CHURN_LABELS == {0: "No", 1: "Yes"}


def test_customers_to_dataframe_builds_dataframe_with_matching_columns(sample_customer):
    df = customers_to_dataframe([sample_customer])

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == list(sample_customer.keys())
    assert df.iloc[0].to_dict() == sample_customer


def test_customers_to_dataframe_preserves_order_for_multiple_customers(sample_customer):
    second_customer = dict(sample_customer, tenure_months=42)
    df = customers_to_dataframe([sample_customer, second_customer])

    assert df["tenure_months"].tolist() == [sample_customer["tenure_months"], 42]


def test_predict_churn_maps_predicted_class_to_label(sample_customer):
    feature_names = build_feature_names([sample_customer])
    model = FakeModel(feature_names, predictions=[0], probabilities=[[0.8, 0.2]])

    results = predict_churn(model, [sample_customer])

    assert results == [{"churn": "No", "probabilidade_churn": 0.2, "confianca": 0.8}]


def test_predict_churn_maps_positive_prediction_to_yes(sample_customer):
    feature_names = build_feature_names([sample_customer])
    model = FakeModel(feature_names, predictions=[1], probabilities=[[0.35, 0.65]])

    results = predict_churn(model, [sample_customer])

    assert results == [{"churn": "Yes", "probabilidade_churn": 0.65, "confianca": 0.65}]


def test_predict_churn_rounds_probabilities_to_four_decimals(sample_customer):
    feature_names = build_feature_names([sample_customer])
    model = FakeModel(feature_names, predictions=[1], probabilities=[[0.111111, 0.888889]])

    results = predict_churn(model, [sample_customer])

    assert results[0]["probabilidade_churn"] == 0.8889
    assert results[0]["confianca"] == 0.8889


def test_predict_churn_preserves_input_order_for_batches(sample_customer):
    second_customer = dict(sample_customer, gender="Male")
    customers = [sample_customer, second_customer]
    feature_names = build_feature_names(customers)
    model = FakeModel(
        feature_names,
        predictions=[0, 1],
        probabilities=[[0.9, 0.1], [0.2, 0.8]],
    )

    results = predict_churn(model, customers)

    assert [r["churn"] for r in results] == ["No", "Yes"]
    assert len(results) == 2
