from fastapi import APIRouter

from app.service_client import patient_client

router = APIRouter(prefix="/care-gaps", tags=["care_gaps"])

@router.get("/gap/{gap_id}")
async def get_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "retrieved"}

@router.post("/{gap_id}/verify")
async def verify_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "verified"}

@router.post("/{gap_id}/dismiss")
async def dismiss_care_gap(gap_id: str):
    return {"gap_id": gap_id, "status": "dismissed"}


@router.get("/{patient_id}")
async def get_patient_care_gaps(patient_id: str):
    patient_state = await patient_client.request("GET", f"/patients/{patient_id}/state")
    return {
        "patient_id": patient_id,
        "care_gaps": [],
        "patient_state_summary": patient_state.get("summary", {}),
        "status": "agent_integration_pending",
    }
