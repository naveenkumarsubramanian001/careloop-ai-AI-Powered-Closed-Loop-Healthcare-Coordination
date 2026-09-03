from fastapi import FastAPI, BackgroundTasks
from app.extraction.ocr import extract_text
from app.extraction.llm_extractor import extract_clinical_events
import uuid

app = FastAPI(title="CareLoop Document Intelligence Service")

@app.post("/process/{document_id}")
async def process_document(document_id: str, background_tasks: BackgroundTasks):
    """Trigger processing for a document."""
    
    # In a real app this would read from storage or queue, here we just trigger immediately
    def _process():
        # Mocking file path
        text = extract_text(f"mock/path/{document_id}.pdf")
        events = extract_clinical_events(text)
        print(f"Processed document {document_id}, extracted events: {events}")
        # Here we would send these events to the Patient State Service
        
    background_tasks.add_task(_process)
    return {"status": "processing_started", "document_id": document_id}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "document-intelligence"}
