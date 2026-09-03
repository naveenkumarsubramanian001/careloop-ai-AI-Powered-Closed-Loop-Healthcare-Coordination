from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/")
async def create_task():
    return {"status": "task created"}

@router.get("/")
async def list_tasks():
    return {"tasks": []}

@router.get("/{task_id}")
async def get_task(task_id: str):
    return {"task_id": task_id, "status": "retrieved"}

@router.patch("/{task_id}")
async def update_task(task_id: str):
    return {"task_id": task_id, "status": "updated"}

@router.post("/{task_id}/complete")
async def complete_task(task_id: str):
    return {"task_id": task_id, "status": "completed"}
