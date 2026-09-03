from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.services.minio_client import minio_client
from app.repositories.document_repo import document_repo

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/")
async def upload_document(patient_id: str = Form(...), file: UploadFile = File(...)):
    file_bytes = await file.read()
    storage_path = minio_client.upload_file(patient_id, file.filename, file_bytes)
    doc_metadata = document_repo.create_document(patient_id, file.filename, storage_path)
    
    # Ideally emit an event to Document Intelligence Service here via Redis
    
    return {"status": "success", "document": doc_metadata}

@router.get("/{document_id}")
async def get_document(document_id: str):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/patients/{patient_id}/documents")
async def get_patient_documents(patient_id: str):
    docs = document_repo.get_patient_documents(patient_id)
    return {"patient_id": patient_id, "documents": docs}

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    minio_client.delete_file(doc["storage_path"])
    document_repo.delete_document(document_id)
    return {"status": "deleted", "document_id": document_id}
