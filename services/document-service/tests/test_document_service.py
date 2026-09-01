from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.document import DocumentResponse

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_document_requires_patient_id():
    response = client.post(
        "/documents",
        data={"patient_id": "   "},
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Patient ID is required."


def test_upload_document_returns_created_document(monkeypatch):
    async def fake_upload_document(self, patient_id: str, file):
        return DocumentResponse(
            id="doc_abc123",
            patient_id=patient_id,
            filename="sample.pdf",
            content_type="application/pdf",
            size=12,
            storage_key=f"patients/{patient_id}/doc_abc123/sample.pdf",
            status="uploaded",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )

    monkeypatch.setattr(
        "app.services.document_service.DocumentService.upload_document",
        fake_upload_document,
    )

    response = client.post(
        "/documents",
        data={"patient_id": "patient-123"},
        files={"file": ("sample.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["patient_id"] == "patient-123"
    assert payload["filename"] == "sample.pdf"
    assert payload["status"] == "uploaded"
