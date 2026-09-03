from fastapi import APIRouter

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    return {"patient_id": patient_id, "status": "retrieved"}

@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    return {"patient_id": patient_id, "timeline": []}

@router.get("/{patient_id}/state")
async def get_patient_state(patient_id: str):
    return {"patient_id": patient_id, "state": "retrieved"}

@router.get("/{patient_id}/documents")
async def get_patient_documents(patient_id: str):
    return {"patient_id": patient_id, "documents": []}
