from fastapi.testclient import TestClient

from app.main import app
from app.models.task import TaskModel


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "task-service"}


def test_task_model_create_filter_and_update():
    store = TaskModel()
    created = store.create_task("P001", "Call patient", priority="High", gap_id="gap-1")

    assert created["status"] == "OPEN"
    assert store.get_all_tasks(patient_id="P001")[0]["id"] == created["id"]

    updated = store.update_task(created["id"], status="COMPLETED", assigned_to="Nurse")

    assert updated["status"] == "COMPLETED"
    assert updated["assigned_to"] == "Nurse"


def test_create_and_complete_task_routes():
    created = client.post(
        "/tasks/",
        json={"patient_id": "P001", "description": "Confirm cardiology visit", "priority": "High"},
    )
    assert created.status_code == 200
    task_id = created.json()["task"]["id"]

    completed = client.post(f"/tasks/{task_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["task"]["status"] == "COMPLETED"


def test_invalid_task_priority_returns_validation_error():
    response = client.post(
        "/tasks/",
        json={"patient_id": "P001", "description": "Bad priority", "priority": "Immediate"},
    )

    assert response.status_code == 422


def test_unknown_task_returns_404():
    response = client.get("/tasks/not-found")

    assert response.status_code == 404
