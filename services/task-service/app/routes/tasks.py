from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.task import task_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    patient_id: str
    description: str
    priority: str = "Medium"

@router.post("/")
async def create_task(task_in: TaskCreate):
    task = task_db.create_task(task_in.patient_id, task_in.description, task_in.priority)
    return {"status": "task created", "task": task}

@router.get("/")
async def list_tasks():
    return {"tasks": task_db.get_all_tasks()}

@router.get("/{task_id}")
async def get_task(task_id: str):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

class TaskUpdate(BaseModel):
    status: str

@router.patch("/{task_id}")
async def update_task(task_id: str, task_in: TaskUpdate):
    task = task_db.update_task_status(task_id, task_in.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "task updated", "task": task}

@router.post("/{task_id}/complete")
async def complete_task(task_id: str):
    task = task_db.update_task_status(task_id, "COMPLETED")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "task completed", "task": task}
