from fastapi.testclient import TestClient

from app import main
from app.extraction.llm_extractor import _fallback_extract_events, extract_clinical_events
from app.main import ProcessRequest, app, process_document_sync


client = TestClient(app)


class FailingModel:
    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        raise RuntimeError("model offline")


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "document-intelligence"}


def test_process_document_endpoint_enqueues_background_work(monkeypatch):
    calls = []

    def fake_process(document_id, request):
        calls.append((document_id, request.patient_id))

    monkeypatch.setattr(main, "process_document_sync", fake_process)

    response = client.post(
        "/process/doc-1",
        json={"patient_id": "P001", "file_path": "mock/path/doc-1.pdf", "publish_events": False},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processing_started"
    assert calls == [("doc-1", "P001")]


def test_extract_clinical_events_uses_fallback_on_model_failure():
    events = extract_clinical_events("Cardiology referral. HbA1c ordered.", model=FailingModel())

    assert {event["event_type"] for event in events} == {"referral", "investigation"}


def test_fallback_extract_events_returns_empty_for_unrelated_text():
    assert _fallback_extract_events("No operational care intent here.") == []


def test_process_document_sync_runs_graph_without_publishing(monkeypatch):
    monkeypatch.setattr(main, "extract_text", lambda path: "HbA1c ordered.")
    monkeypatch.setattr(main, "extract_clinical_events", lambda text: [{"event_type": "investigation", "test": "HbA1c"}])

    result = process_document_sync(
        "doc-1",
        ProcessRequest(patient_id="P001", file_path="mock/path/doc-1.pdf", publish_events=False),
    )

    assert result["document_id"] == "doc-1"
    assert result["events"] == [{"event_type": "investigation", "test": "HbA1c"}]
    assert result["published_count"] == 0
