import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.models.task import VALID_PRIORITIES, VALID_STATUSES, task_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    patient_id: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=2000)
    priority: str = "Medium"
    gap_id: Optional[str] = None
    assigned_to: str = "Care Coordinator"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return value

@router.post("/")
async def create_task(task_in: TaskCreate):
    task = task_db.create_task(
        patient_id=task_in.patient_id.strip(),
        description=task_in.description.strip(),
        priority=task_in.priority,
        gap_id=task_in.gap_id,
        assigned_to=task_in.assigned_to.strip() or "Care Coordinator",
    )
    logger.info("task_created", extra={"task_id": task["id"], "patient_id": task["patient_id"]})
    return {"status": "task created", "task": task}

@router.get("/")
async def list_tasks(
    patient_id: Optional[str] = None,
    status: Optional[str] = Query(default=None),
):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {sorted(VALID_STATUSES)}")
    return {"tasks": task_db.get_all_tasks(patient_id=patient_id, status=status)}

@router.get("/{task_id}")
async def get_task(task_id: str):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return value

    @field_validator("priority")
    @classmethod
    def validate_update_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return value

@router.patch("/{task_id}")
async def update_task(task_id: str, task_in: TaskUpdate):
    if not task_in.model_fields_set:
        raise HTTPException(status_code=400, detail="At least one task field must be provided.")

    task = task_db.update_task(
        task_id,
        status=task_in.status,
        priority=task_in.priority,
        assigned_to=task_in.assigned_to,
        description=task_in.description.strip() if task_in.description else None,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info("task_updated", extra={"task_id": task_id, "status": task["status"]})
    return {"status": "task updated", "task": task}

@router.post("/{task_id}/complete")
async def complete_task(task_id: str):
    task = task_db.update_task_status(task_id, "COMPLETED")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "task completed", "task": task}
