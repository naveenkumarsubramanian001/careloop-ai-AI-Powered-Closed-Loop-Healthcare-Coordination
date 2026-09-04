from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.service_client import task_client

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    patient_id: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=2000)
    priority: str = "Medium"
    gap_id: Optional[str] = None
    assigned_to: str = "Care Coordinator"


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)


@router.post("/")
async def create_task(task_in: TaskCreate):
    return await task_client.request("POST", "/tasks/", json=task_in.model_dump())

@router.get("/")
async def list_tasks(patient_id: Optional[str] = None, status: Optional[str] = Query(default=None)):
    params = {key: value for key, value in {"patient_id": patient_id, "status": status}.items() if value is not None}
    return await task_client.request("GET", "/tasks/", params=params)

@router.get("/{task_id}")
async def get_task(task_id: str):
    return await task_client.request("GET", f"/tasks/{task_id}")

@router.patch("/{task_id}")
async def update_task(task_id: str, task_in: TaskUpdate):
    return await task_client.request("PATCH", f"/tasks/{task_id}", json=task_in.model_dump(exclude_none=True))

@router.post("/{task_id}/complete")
async def complete_task(task_id: str):
    return await task_client.request("POST", f"/tasks/{task_id}/complete")
