from fastapi.testclient import TestClient

from app.main import app
from app.models.patient import PatientModel


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "patient-state"}


def test_patient_model_builds_sorted_state():
    store = PatientModel()
    store.add_patient("P100", {"name": "Jane Doe"})
    store.add_event("P100", {"event_type": "lab_result", "test": "HbA1c", "date": "2026-08-05"})
    store.add_event("P100", {"event_type": "lab_order", "test": "HbA1c", "date": "2026-08-01"})

    state = store.build_state("P100")

    assert state["summary"]["total_events"] == 2
    assert state["events"][0]["event_type"] == "lab_order"
    assert state["summary"]["closing_event_count"] == 1


def test_upsert_and_add_event_routes():
    upsert = client.put("/patients/P200", json={"name": "Patient Two", "metadata": {"risk": "medium"}})
    assert upsert.status_code == 200

    event = client.post(
        "/patients/P200/events",
        json={"event_type": "referral", "specialty": "cardiology", "date": "2026-08-04"},
    )
    assert event.status_code == 200

    state = client.get("/patients/P200/state")
    assert state.status_code == 200
    assert state.json()["summary"]["open_intent_count"] == 1


def test_add_event_returns_404_for_unknown_patient():
    response = client.post("/patients/unknown/events", json={"event_type": "referral"})

    assert response.status_code == 404
