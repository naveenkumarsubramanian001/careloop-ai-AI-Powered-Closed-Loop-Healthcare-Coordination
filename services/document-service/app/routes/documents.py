import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])
_document_service = DocumentService()


def get_document_service() -> DocumentService:
    return _document_service


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(patient_id: str = Form(...), file: UploadFile = File(...)):
    try:
        document = await get_document_service().upload_document(patient_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("document_upload_route_failed")
        raise HTTPException(status_code=502, detail="Document upload failed.") from exc

    return document


@router.get("/patients/{patient_id}/documents")
async def get_patient_documents(patient_id: str):
    docs = await get_document_service().get_patient_documents(patient_id)
    return {"patient_id": patient_id, "documents": docs}

@router.get("/{document_id}")
async def get_document(document_id: str):
    doc = await get_document_service().get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    deleted = await get_document_service().delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}
