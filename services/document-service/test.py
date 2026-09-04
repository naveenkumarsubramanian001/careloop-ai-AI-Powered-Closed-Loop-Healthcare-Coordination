from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "document-service"}


def test_safe_filename_strips_path_segments():
    assert DocumentService._safe_filename("../../report.pdf") == "report.pdf"


def test_safe_filename_rejects_empty_names():
    with pytest.raises(ValueError):
        DocumentService._safe_filename("   ")


def test_upload_document_returns_created_document(monkeypatch):
    async def fake_upload_document(self, patient_id, file):
        now = datetime.now(timezone.utc)
        return DocumentResponse(
            id="doc_abc123",
            patient_id=patient_id.strip(),
            filename="sample.pdf",
            content_type="application/pdf",
            size=12,
            storage_key=f"patients/{patient_id.strip()}/doc_abc123/sample.pdf",
            status="uploaded",
            created_at=now,
            updated_at=now,
        )

    monkeypatch.setattr(DocumentService, "upload_document", fake_upload_document)

    response = client.post(
        "/documents/",
        data={"patient_id": "patient-123"},
        files={"file": ("sample.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json()["patient_id"] == "patient-123"


def test_upload_document_validation_error_becomes_400(monkeypatch):
    async def fake_upload_document(self, patient_id, file):
        raise ValueError("File is empty.")

    monkeypatch.setattr(DocumentService, "upload_document", fake_upload_document)

    response = client.post(
        "/documents/",
        data={"patient_id": "patient-123"},
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File is empty."


def test_get_patient_documents_uses_service(monkeypatch):
    async def fake_get_patient_documents(self, patient_id):
        return []

    monkeypatch.setattr(DocumentService, "get_patient_documents", fake_get_patient_documents)

    response = client.get("/documents/patients/P001/documents")

    assert response.status_code == 200
    assert response.json() == {"patient_id": "P001", "documents": []}
