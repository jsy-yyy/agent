from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.core.errors import AppError
from app.core.task_status import TaskStatus
from app.schemas.tasks import TaskResponse


class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskResponse] = {}

    def create_simulated_task(self) -> TaskResponse:
        now = self._now()
        task = TaskResponse(
            task_id=f"task_{uuid4().hex}",
            task_type="simulated",
            status=TaskStatus.PENDING,
            progress=0,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> TaskResponse:
        task = self._tasks.get(task_id)
        if task is None:
            raise AppError(
                message=f"Task '{task_id}' was not found.",
                code="task_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return task

    def fail_task(self, task_id: str, error_message: str) -> TaskResponse:
        task = self.get_task(task_id)
        updated = task.model_copy(
            update={
                "status": TaskStatus.FAILED,
                "progress": task.progress,
                "error_message": error_message,
                "updated_at": self._now(),
            }
        )
        self._tasks[task_id] = updated
        return updated

    def reset(self) -> None:
        self._tasks.clear()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)


task_service = TaskService()
