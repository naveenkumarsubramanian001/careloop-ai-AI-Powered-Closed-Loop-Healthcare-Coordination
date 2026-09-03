from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/")
async def upload_document():
    # Logic to route to Document Service
    return {"status": "document uploaded"}

@router.get("/{document_id}")
async def get_document(document_id: str):
    return {"document_id": document_id, "status": "retrieved"}

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    return {"document_id": document_id, "status": "deleted"}
