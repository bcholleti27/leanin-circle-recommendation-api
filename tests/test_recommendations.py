
from datetime import UTC, datetime

import pytest

from app.data_loader import load_all_data
from app.recommendations import (
    get_eligible_circles,
    recommend_circles,
)

REFERENCE_DATE = datetime(
    2026, 9, 21, tzinfo=UTC
)


@pytest.fixture
def data():
    return load_all_data()


def test_full_and_inactive_circles_are_excluded(data):
    eligible = get_eligible_circles(
        23, data, as_of=REFERENCE_DATE
    )
    eligible_ids = {circle["id"] for circle in eligible}

    assert 20 not in eligible_ids
    assert 21 not in eligible_ids
    assert 22 in eligible_ids


def test_cold_start_returns_recommendations(data):
    results = recommend_circles(
        42, data, as_of=REFERENCE_DATE
    )

    assert len(results) == 5
    assert all("reason" in item for item in results)


def test_topic_diversity(data):
    results = recommend_circles(
        15, data, as_of=REFERENCE_DATE
    )

    negotiation_count = sum(
        item["topic"] == "negotiation"
        for item in results
    )

    assert negotiation_count <= 2


def test_already_joined_circles_are_excluded(data):
    results = recommend_circles(
        7, data, limit=20, as_of=REFERENCE_DATE
    )

    joined_ids = {
        membership["circle_id"]
        for membership in data["memberships"]
        if membership["user_id"] == 7
    }

    assert all(
        item["circle_id"] not in joined_ids
        for item in results
    )


def test_unknown_user_raises_error(data):
    with pytest.raises(ValueError, match="not found"):
        recommend_circles(
            999999, data, as_of=REFERENCE_DATE
        )


from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommendations_endpoint():
    response = client.get(
        "/users/23/recommendations?limit=5"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == 23
    assert body["count"] == 5
    assert body["recommendations"][0]["circle_id"] == 22
    assert all(
        "reason" in item
        for item in body["recommendations"]
    )


def test_unknown_user_returns_404():
    response = client.get(
        "/users/999999/recommendations"
    )

    assert response.status_code == 404


def test_invalid_limit_returns_422():
    response = client.get(
        "/users/23/recommendations?limit=0"
    )

    assert response.status_code == 422
