from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional
import uuid


VALID_STATUSES = {"OPEN", "IN_PROGRESS", "BLOCKED", "COMPLETED", "CANCELLED"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}


class TaskModel:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def create_task(
        self,
        patient_id: str,
        description: str,
        priority: str = "Medium",
        gap_id: Optional[str] = None,
        assigned_to: str = "Care Coordinator",
    ) -> Dict[str, Any]:
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")

        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        task = {
            "id": task_id,
            "patient_id": patient_id,
            "gap_id": gap_id,
            "description": description,
            "priority": priority,
            "status": "OPEN",
            "assigned_to": assigned_to or "Care Coordinator",
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self.tasks[task_id] = task
            return deepcopy(task)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self.tasks.get(task_id)
            return deepcopy(task) if task else None

    def get_all_tasks(self, patient_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            tasks = list(self.tasks.values())
        if patient_id:
            tasks = [task for task in tasks if task["patient_id"] == patient_id]
        if status:
            tasks = [task for task in tasks if task["status"] == status]
        return [deepcopy(task) for task in sorted(tasks, key=lambda item: item["updated_at"], reverse=True)]

    def update_task(
        self,
        task_id: str,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if status is not None and status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        if priority is not None and priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")

        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            if status is not None:
                task["status"] = status
            if priority is not None:
                task["priority"] = priority
            if assigned_to is not None:
                task["assigned_to"] = assigned_to
            if description is not None:
                task["description"] = description
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            return deepcopy(task)

    def update_task_status(self, task_id: str, status: str) -> Optional[Dict[str, Any]]:
        return self.update_task(task_id, status=status)

task_db = TaskModel()
