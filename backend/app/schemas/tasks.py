from datetime import datetime

from pydantic import BaseModel, Field

from app.core.task_status import TaskStatus


class TaskFailRequest(BaseModel):
    error_message: str = Field(min_length=1)


class TaskResponse(BaseModel):
    task_id: str
    task_type: str
    status: TaskStatus
    progress: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
