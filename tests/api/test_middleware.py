from __future__ import annotations


def test_response_includes_trace_id_and_timing_headers(client):
    response = client.get("/")

    assert response.status_code == 200
    assert len(response.headers["X-Trace-ID"]) == 8
    assert float(response.headers["X-Response-Time-Ms"]) >= 0


def test_each_request_gets_a_distinct_trace_id(client):
    first = client.get("/")
    second = client.get("/")

    assert first.headers["X-Trace-ID"] != second.headers["X-Trace-ID"]
