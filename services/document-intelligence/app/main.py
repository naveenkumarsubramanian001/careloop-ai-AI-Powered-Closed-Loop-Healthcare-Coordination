import logging
import os
from typing import Any, Dict, List, TypedDict

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.extraction.ocr import extract_text
from app.extraction.llm_extractor import extract_clinical_events

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(title="CareLoop Document Intelligence Service")


class ProcessRequest(BaseModel):
    patient_id: str = Field(min_length=1)
    storage_key: str | None = None
    file_path: str | None = None
    publish_events: bool = True


class ProcessingState(TypedDict):
    document_id: str
    patient_id: str
    file_path: str
    text: str
    events: List[Dict[str, Any]]
    published_count: int
    errors: List[str]


def resolve_document_node(state: ProcessingState) -> Dict[str, Any]:
    file_path = state.get("file_path") or f"mock/path/{state['document_id']}.pdf"
    return {"file_path": file_path}


def ocr_node(state: ProcessingState) -> Dict[str, Any]:
    try:
        return {"text": extract_text(state["file_path"])}
    except Exception as exc:
        logger.exception("ocr_failed", extra={"document_id": state["document_id"]})
        return {"text": "", "errors": [*state.get("errors", []), f"ocr_failed: {exc}"]}


def event_extraction_node(state: ProcessingState) -> Dict[str, Any]:
    try:
        events = extract_clinical_events(state.get("text", ""))
    except Exception as exc:
        logger.exception("event_extraction_failed", extra={"document_id": state["document_id"]})
        return {"events": [], "errors": [*state.get("errors", []), f"event_extraction_failed: {exc}"]}
    return {"events": events}


builder = StateGraph(ProcessingState)
builder.add_node("resolve_document", resolve_document_node)
builder.add_node("ocr", ocr_node)
builder.add_node("extract_events", event_extraction_node)
builder.add_edge(START, "resolve_document")
builder.add_edge("resolve_document", "ocr")
builder.add_edge("ocr", "extract_events")
builder.add_edge("extract_events", END)
processing_graph = builder.compile()


def process_document_sync(document_id: str, request: ProcessRequest) -> Dict[str, Any]:
    initial_state = {
        "document_id": document_id,
        "patient_id": request.patient_id,
        "file_path": request.file_path or request.storage_key or "",
        "text": "",
        "events": [],
        "published_count": 0,
        "errors": [],
    }
    result = processing_graph.invoke(initial_state)
    if request.publish_events:
        result["published_count"] = publish_events(request.patient_id, result.get("events", []))
    logger.info(
        "document_processed",
        extra={"document_id": document_id, "patient_id": request.patient_id, "events": len(result.get("events", []))},
    )
    return result


def publish_events(patient_id: str, events: List[Dict[str, Any]]) -> int:
    if not events:
        return 0
    base_url = os.getenv("PATIENT_STATE_URL", "http://patient-state:8003").rstrip("/")
    published = 0
    with httpx.Client(timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))) as client:
        for event in events:
            try:
                response = client.post(f"{base_url}/patients/{patient_id}/events", json=event)
                response.raise_for_status()
                published += 1
            except httpx.HTTPError as exc:
                logger.warning("publish_event_failed", extra={"patient_id": patient_id, "error": str(exc)})
    return published


@app.post("/process/{document_id}")
async def process_document(document_id: str, request: ProcessRequest, background_tasks: BackgroundTasks):
    """Trigger processing for a document."""
    if not document_id.strip():
        raise HTTPException(status_code=400, detail="document_id is required")

    background_tasks.add_task(process_document_sync, document_id.strip(), request)
    return {"status": "processing_started", "document_id": document_id, "patient_id": request.patient_id}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "document-intelligence"}
