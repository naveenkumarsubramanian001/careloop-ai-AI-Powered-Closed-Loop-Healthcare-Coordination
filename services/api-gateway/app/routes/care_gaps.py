from fastapi import APIRouter

router = APIRouter(prefix="/care-gaps", tags=["care_gaps"])

@router.get("/{patient_id}")
async def get_patient_care_gaps(patient_id: str):
    return {"patient_id": patient_id, "care_gaps": []}

@router.get("/gap/{gap_id}")
async def get_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "retrieved"}

@router.post("/{gap_id}/verify")
async def verify_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "verified"}

@router.post("/{gap_id}/dismiss")
async def dismiss_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "dismissed"}
