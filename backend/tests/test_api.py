"""
Basic API tests for HoopMind AI backend.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "HoopMind AI"
    assert data["status"] == "operational"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_docs_available():
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_schema():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "/players/" in schema["paths"]
    assert "/analytics/shot-probability" in schema["paths"]


def test_shot_probability_schema():
    """Test shot probability endpoint accepts valid input."""
    payload = {
        "shot_distance": 25.0,
        "shot_angle": 10.0,
        "shot_type": "Jump Shot",
        "is_three_pointer": True,
        "is_catch_and_shoot": True,
        "defender_distance": 4.0,
        "quarter": 3,
        "time_remaining_seconds": 300.0,
        "shot_clock": 15.0,
        "is_home": True,
        "dribbles_before_shot": 0,
        "touch_time": 1.2,
    }
    # Will return 503 if models not trained, but shouldn't 422
    r = client.post("/analytics/shot-probability", json=payload)
    assert r.status_code in [200, 503]


def test_shot_probability_invalid_distance():
    """Reject invalid shot distance."""
    payload = {
        "shot_distance": -5.0,  # invalid
        "shot_angle": 0.0,
        "shot_type": "Jump Shot",
        "is_three_pointer": False,
        "defender_distance": 4.0,
        "quarter": 1,
        "time_remaining_seconds": 600.0,
    }
    r = client.post("/analytics/shot-probability", json=payload)
    assert r.status_code == 422


def test_win_probability_missing_teams():
    r = client.post("/analytics/win-probability", json={"home_team_id": 9999, "away_team_id": 9998})
    assert r.status_code in [404, 503]
