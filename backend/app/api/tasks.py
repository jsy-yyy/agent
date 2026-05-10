from fastapi import APIRouter

from app.schemas.tasks import TaskFailRequest, TaskResponse
from app.services.task_service import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/simulated", response_model=TaskResponse, status_code=201)
def create_simulated_task() -> TaskResponse:
    return task_service.create_simulated_task()


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: str) -> TaskResponse:
    return task_service.get_task(task_id)


@router.post("/{task_id}/fail", response_model=TaskResponse)
def fail_task(task_id: str, request: TaskFailRequest) -> TaskResponse:
    return task_service.fail_task(task_id=task_id, error_message=request.error_message)
