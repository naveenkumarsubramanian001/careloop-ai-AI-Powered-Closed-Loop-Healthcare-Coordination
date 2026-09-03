from fastapi import APIRouter, HTTPException
from app.models.patient import patient_db

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    patient = patient_db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    events = patient_db.get_events(patient_id)
    # Sort events by date if available to reconstruct a timeline
    sorted_events = sorted(events, key=lambda x: x.get("date", ""))
    return {"patient_id": patient_id, "timeline": sorted_events}

@router.get("/{patient_id}/state")
async def get_patient_state(patient_id: str):
    patient = patient_db.get_patient(patient_id)
    events = patient_db.get_events(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Simple state aggregator for demo
    return {
        "patient_id": patient_id, 
        "state": {
            "total_events": len(events),
            "recent_event": events[-1] if events else None
        }
    }
