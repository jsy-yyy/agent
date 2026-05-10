from datetime import datetime
from uuid import uuid4

from fastapi import status

from app.core.errors import AppError
from app.core.task_status import TaskStatus
from app.schemas.tasks import TaskResponse
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect, initialize_database


class TaskService:
    def create_task(self, task_type: str, *, status: TaskStatus = TaskStatus.PENDING) -> TaskResponse:
        task_id = f"task_{uuid4().hex}"
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    task_id, task_type, status, progress, error_message,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    task_type,
                    status.value,
                    0,
                    None,
                    to_storage_time(now),
                    to_storage_time(now),
                ),
            )
        return self.get_task(task_id)

    def create_simulated_task(self) -> TaskResponse:
        return self.create_task("simulated")

    def update_task(
        self,
        task_id: str,
        *,
        status: TaskStatus,
        progress: int,
        error_message: str | None = None,
    ) -> TaskResponse:
        self.get_task(task_id)
        with connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET status = ?, progress = ?, error_message = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (
                    status.value,
                    progress,
                    error_message,
                    to_storage_time(utc_now()),
                    task_id,
                ),
            )
        return self.get_task(task_id)

    def get_task(self, task_id: str) -> TaskResponse:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise AppError(
                message=f"Task '{task_id}' was not found.",
                code="task_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._task_from_row(row)

    def fail_task(self, task_id: str, error_message: str) -> TaskResponse:
        return self.update_task(
            task_id,
            status=TaskStatus.FAILED,
            progress=self.get_task(task_id).progress,
            error_message=error_message,
        )

    def reset(self) -> None:
        initialize_database()
        with connect() as connection:
            connection.execute("DELETE FROM tasks")

    @staticmethod
    def _task_from_row(row) -> TaskResponse:
        return TaskResponse(
            task_id=row["task_id"],
            task_type=row["task_type"],
            status=TaskStatus(row["status"]),
            progress=row["progress"],
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


task_service = TaskService()
