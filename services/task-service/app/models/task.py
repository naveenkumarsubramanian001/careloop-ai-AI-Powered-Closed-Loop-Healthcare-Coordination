from typing import Dict, Any, List
import uuid

class TaskModel:
    def __init__(self):
        self.tasks = {}

    def create_task(self, patient_id: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "patient_id": patient_id,
            "description": description,
            "priority": priority,
            "status": "OPEN",
            "assigned_to": "Care Coordinator"
        }
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Dict[str, Any]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks.values())

    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            return self.tasks[task_id]
        return None

task_db = TaskModel()
