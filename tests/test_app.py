"""
test_app.py
-----------
Unit tests for the Smart Fitness Tracking and Health Monitoring System.

Run with:
    pytest
from the project root directory.
"""

import os
import sys
import sqlite3
import pytest

# Make the project root importable when running `pytest` from the root folder.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as flask_app_module  # noqa: E402


@pytest.fixture
def client():
    flask_app_module.app.config["TESTING"] = True
    flask_app_module.init_db()
    with flask_app_module.app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Smart Fitness" in response.data


def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_activity_page_get(client):
    response = client.get("/activity")
    assert response.status_code == 200


def test_activity_log_post(client):
    response = client.post(
        "/activity",
        data={"activity_type": "Running", "duration_minutes": "20"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Running" in response.data


def test_prediction_page_get(client):
    response = client.get("/predict")
    assert response.status_code == 200


def test_prediction_low_risk(client):
    response = client.post(
        "/predict",
        data={
            "age": "25", "heart_rate": "70", "spo2": "98",
            "sleep_hours": "8", "bmi": "21", "activity_level": "high",
        },
    )
    assert response.status_code == 200
    assert b"Risk" in response.data


def test_prediction_high_risk_triggers_alert(client):
    response = client.post(
        "/predict",
        data={
            "age": "65", "heart_rate": "135", "spo2": "89",
            "sleep_hours": "3", "bmi": "33", "activity_level": "low",
        },
    )
    assert response.status_code == 200

    alerts_response = client.get("/alerts")
    assert alerts_response.status_code == 200
    assert b"High" in alerts_response.data or b"Alert" in alerts_response.data


def test_recommendations_page(client):
    response = client.get("/recommendations")
    assert response.status_code == 200
    assert b"Recommendations" in response.data


def test_alerts_page(client):
    response = client.get("/alerts")
    assert response.status_code == 200


def test_health_check_api(client):
    response = client.get("/api/health-check")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_database_tables_exist():
    db_path = flask_app_module.DB_PATH
    assert os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    conn.close()

    expected = {"users", "health_records", "activities", "recommendations", "alerts"}
    assert expected.issubset(tables)


def test_generate_alerts_logic():
    alerts = flask_app_module.generate_alerts(heart_rate=150, spo2=85, sleep_hours=2)
    assert len(alerts) == 3


def test_generate_alerts_no_issues():
    alerts = flask_app_module.generate_alerts(heart_rate=75, spo2=98, sleep_hours=8)
    assert len(alerts) == 0


def test_health_model_prediction():
    from models.health_model import HealthRiskModel

    model = HealthRiskModel()
    model.train()
    result = model.predict(
        age=30, heart_rate=75, spo2=97, sleep_hours=7, activity_level=1, bmi=22
    )
    assert result in ("Low", "Moderate", "High")
