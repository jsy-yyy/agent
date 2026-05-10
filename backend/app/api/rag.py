from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.errors import AppError
from app.services.embedding.index_service import IndexService
from app.services.llm import LLMService
from app.services.rag_pipeline import RagPipeline
from app.services.textbook_service import textbook_service

router = APIRouter(prefix="/api/rag")


class IndexRequest(BaseModel):
    textbook_id: str


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


def _get_llm(request: Request) -> LLMService:
    return request.app.state.llm_service


def _get_index(request: Request) -> IndexService:
    return request.app.state.index_service


@router.post("/index")
def build_index(request: Request, body: IndexRequest) -> dict:
    llm = _get_llm(request)
    index_svc = _get_index(request)
    chapters = textbook_service.list_chapters(body.textbook_id)
    if not chapters:
        raise AppError(message="No parsed chapters to index.", code="no_chapters")

    pipeline = RagPipeline(llm, index_svc)
    chunks = pipeline.index_chapters(body.textbook_id, chapters)
    return {"textbook_id": body.textbook_id, "chunk_count": len(chunks), "status": "indexed"}


@router.get("/status")
def get_status(request: Request) -> dict:
    index_svc = _get_index(request)
    return {"indexed_chunks": index_svc.size, "is_loaded": index_svc.is_loaded}


@router.post("/query")
def query(request: Request, body: QueryRequest) -> dict:
    llm = _get_llm(request)
    index_svc = _get_index(request)

    if not index_svc.is_loaded:
        raise AppError(message="Index is not built. Index a textbook first.", code="index_not_built")

    pipeline = RagPipeline(llm, index_svc)
    return pipeline.answer(body.question, top_k=body.top_k)
