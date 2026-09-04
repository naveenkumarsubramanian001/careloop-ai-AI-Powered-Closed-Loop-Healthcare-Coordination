import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.routes import patients as patient_routes
from app.routes import tasks as task_routes
from app.main import app
from app.service_client import ServiceClient


client = TestClient(app)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api-gateway"}


@pytest.mark.anyio
async def test_service_client_translates_timeout(monkeypatch):
    async def fake_request(self, method, url, **kwargs):
        raise httpx.TimeoutException("slow")

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    with pytest.raises(HTTPException) as exc:
        await ServiceClient("http://example", "example-service").request("GET", "/health")

    assert exc.value.status_code == 504


def test_gateway_patient_route_uses_patient_client(monkeypatch):
    async def fake_request(method, path, **kwargs):
        assert method == "GET"
        assert path == "/patients/P001"
        return {"id": "P001", "name": "Jane"}

    monkeypatch.setattr(patient_routes.patient_client, "request", fake_request)

    response = client.get("/api/patients/P001")

    assert response.status_code == 200
    assert response.json()["id"] == "P001"


def test_gateway_task_creation_proxies_payload(monkeypatch):
    async def fake_request(method, path, **kwargs):
        assert method == "POST"
        assert path == "/tasks/"
        assert kwargs["json"]["description"] == "Call patient"
        return {"status": "task created", "task": {"id": "task-1"}}

    monkeypatch.setattr(task_routes.task_client, "request", fake_request)

    response = client.post(
        "/api/tasks/",
        json={"patient_id": "P001", "description": "Call patient", "priority": "Medium"},
    )

    assert response.status_code == 200
    assert response.json()["task"]["id"] == "task-1"


def test_care_gap_gap_route_is_not_shadowed():
    response = client.get("/api/care-gaps/gap/gap-123")

    assert response.status_code == 200
    assert response.json() == {"gap_id": "gap-123", "status": "retrieved"}
