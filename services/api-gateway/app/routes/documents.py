from fastapi import APIRouter, File, Form, UploadFile

from app.service_client import document_client

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/")
async def upload_document(patient_id: str = Form(...), file: UploadFile = File(...)):
    return await document_client.upload("/documents/", patient_id=patient_id, file=file)

@router.get("/{document_id}")
async def get_document(document_id: str):
    return await document_client.request("GET", f"/documents/{document_id}")

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    return await document_client.request("DELETE", f"/documents/{document_id}")
