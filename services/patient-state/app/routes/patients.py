import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.patient import patient_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patients", tags=["patients"])


class PatientUpsert(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatientEventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    date: str = Field(default="")
    details: Dict[str, Any] = Field(default_factory=dict)
    specialty: str | None = None
    test: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


@router.put("/{patient_id}")
async def upsert_patient(patient_id: str, patient_in: PatientUpsert):
    patient = patient_db.add_patient(
        patient_id.strip(),
        {"name": patient_in.name.strip(), "metadata": patient_in.metadata},
    )
    logger.info("patient_upserted", extra={"patient_id": patient_id})
    return {"status": "patient upserted", "patient": patient}


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    patient = patient_db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/{patient_id}/events")
async def add_patient_event(patient_id: str, event_in: PatientEventCreate):
    try:
        event = patient_db.add_event(
            patient_id,
            {
                "event_type": event_in.event_type.strip().lower(),
                "date": event_in.date,
                "details": event_in.details,
                "specialty": event_in.specialty,
                "test": event_in.test,
                "confidence": event_in.confidence,
            },
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Patient not found")
    logger.info("patient_event_added", extra={"patient_id": patient_id, "event_type": event["event_type"]})
    return {"status": "event added", "event": event}


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    if not patient_db.get_patient(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    events = patient_db.get_events(patient_id)
    # Sort events by date if available to reconstruct a timeline
    sorted_events = sorted(events, key=lambda x: x.get("date", ""))
    return {"patient_id": patient_id, "timeline": sorted_events}

@router.get("/{patient_id}/state")
async def get_patient_state(patient_id: str):
    state = patient_db.build_state(patient_id)
    if not state:
        raise HTTPException(status_code=404, detail="Patient not found")
    return state
