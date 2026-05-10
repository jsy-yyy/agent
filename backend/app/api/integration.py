from fastapi import APIRouter, Request

from app.core.errors import AppError
from app.services.embedding import EmbeddingProviderError
from app.services.embedding.index_service import IndexService
from app.services.integration_engine import IntegrationEngine
from app.services.integration_projection import integration_projection_service
from app.services.integration_service import integration_service
from app.services.llm import LLMProviderError, LLMService
from app.services.task_service import task_service
from app.services.textbook_service import textbook_service

router = APIRouter(prefix="/api/integration")


def _get_llm(request: Request) -> LLMService:
    return request.app.state.llm_service


def _get_index(request: Request) -> IndexService:
    return request.app.state.index_service


@router.post("/run")
def run_integration(request: Request) -> dict:
    llm = _get_llm(request)
    index_svc = _get_index(request)

    textbooks = textbook_service.list_textbooks()
    if len(textbooks) < 2:
        raise AppError(
            message="Need at least 2 parsed textbooks to run integration.",
            code="insufficient_textbooks",
        )

    textbook_ids = [t.textbook_id for t in textbooks if t.parse_status == "parsed"]
    if len(textbook_ids) < 2:
        raise AppError(
            message="Need at least 2 parsed textbooks to run integration.",
            code="insufficient_textbooks",
        )

    task = task_service.create_task(task_type="integration")
    from app.core.task_status import TaskStatus
    task_service.update_task(task.task_id, status=TaskStatus.RUNNING, progress=0)

    engine = IntegrationEngine(llm, index_svc)
    try:
        result = engine.integrate(textbook_ids)
    except EmbeddingProviderError as exc:
        task_service.fail_task(task.task_id, str(exc))
        message = str(exc)
        status_code = 429 if "429" in message or "rate limit" in message.lower() else 503
        raise AppError(
            message=f"Embedding request failed during integration: {message}",
            code="embedding_unavailable",
            status_code=status_code,
        ) from exc
    except LLMProviderError as exc:
        task_service.fail_task(task.task_id, str(exc))
        raise AppError(
            message=f"LLM request failed during integration: {exc}",
            code="llm_unavailable",
            status_code=503,
        ) from exc

    task_service.update_task(task.task_id, status=TaskStatus.COMPLETED, progress=100)

    return {
        "task_id": task.task_id,
        "status": "completed",
        "merge_count": result.merge_count,
        "keep_count": result.keep_count,
        "remove_count": result.remove_count,
        "total_source_chars": result.total_source_chars,
        "integrated_chars": result.integrated_chars,
        "compression_ratio": result.compression_ratio,
        "target_chars": result.target_chars,
        "target_met": result.target_met,
    }


@router.get("/decisions")
def list_decisions() -> dict:
    decisions = integration_service.list_decisions()
    return {"decisions": [d.model_dump(mode="json") for d in decisions]}


@router.get("/stats")
def get_stats() -> dict:
    return integration_projection_service.build_stats().__dict__
