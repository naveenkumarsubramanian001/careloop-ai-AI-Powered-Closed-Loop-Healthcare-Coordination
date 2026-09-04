from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.service_client import document_client, patient_client

router = APIRouter(prefix="/patients", tags=["patients"])


class PatientUpsert(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatientEventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    date: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)
    specialty: str | None = None
    test: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


@router.put("/{patient_id}")
async def upsert_patient(patient_id: str, patient_in: PatientUpsert):
    return await patient_client.request("PUT", f"/patients/{patient_id}", json=patient_in.model_dump())


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    return await patient_client.request("GET", f"/patients/{patient_id}")


@router.post("/{patient_id}/events")
async def add_patient_event(patient_id: str, event_in: PatientEventCreate):
    return await patient_client.request("POST", f"/patients/{patient_id}/events", json=event_in.model_dump())

@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    return await patient_client.request("GET", f"/patients/{patient_id}/timeline")

@router.get("/{patient_id}/state")
async def get_patient_state(patient_id: str):
    return await patient_client.request("GET", f"/patients/{patient_id}/state")

@router.get("/{patient_id}/documents")
async def get_patient_documents(patient_id: str):
    return await document_client.request("GET", f"/documents/patients/{patient_id}/documents")
