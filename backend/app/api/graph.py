from fastapi import APIRouter, Request

from app.core.errors import AppError
from app.core.task_status import TaskStatus
from app.schemas.graph import BuildGraphRequest, BuildGraphResponse, GraphDataResponse, GraphEdgeResponse, GraphNodeResponse
from app.services.graph_service import graph_service
from app.services.integration_projection import integration_projection_service
from app.services.knowledge_extractor import KnowledgeExtractor
from app.services.llm import LLMService
from app.services.task_service import task_service
from app.services.textbook_service import textbook_service

router = APIRouter(prefix="/api/graph")


def _get_llm_service(request: Request) -> LLMService:
    return request.app.state.llm_service


@router.post("/build", response_model=BuildGraphResponse)
def build_graph(request: Request, body: BuildGraphRequest) -> BuildGraphResponse:
    llm = _get_llm_service(request)
    try:
        textbook = textbook_service.get_textbook(body.textbook_id)
    except KeyError:
        raise AppError(message=f"Textbook '{body.textbook_id}' was not found.", code="textbook_not_found", status_code=404)
    chapters = textbook_service.list_chapters(body.textbook_id)
    if not chapters:
        raise AppError(message=f"Textbook '{textbook.title}' has no parsed chapters.", code="no_chapters")

    task = task_service.create_task(task_type="graph_extraction")
    task_service.update_task(task.task_id, status=TaskStatus.RUNNING, progress=0)

    extractor = KnowledgeExtractor(llm)
    result = extractor.extract(body.textbook_id, chapters)

    if result.node_count == 0 and result.edge_count == 0:
        task_service.update_task(
            task.task_id, status=TaskStatus.FAILED, progress=100,
            error_message="No knowledge points extracted.",
        )
    else:
        task_service.update_task(task.task_id, status=TaskStatus.COMPLETED, progress=100)

    return BuildGraphResponse(
        textbook_id=body.textbook_id,
        task_id=task.task_id,
        status="completed" if result.node_count > 0 else "failed",
    )


@router.get("/merged", response_model=GraphDataResponse)
def get_merged_graph() -> GraphDataResponse:
    graph = integration_projection_service.build_merged_graph()
    return GraphDataResponse(
        textbook_id="merged",
        nodes=[
            GraphNodeResponse(
                node_id=node.node_id,
                textbook_id=node.textbook_id,
                chapter_id=node.chapter_id,
                name=node.name,
                definition=node.definition,
                category=node.category,
                page=node.page,
                source_excerpt=node.source_excerpt,
                frequency=node.frequency,
            )
            for node in graph.nodes
        ],
        edges=[
            GraphEdgeResponse(
                edge_id=edge.edge_id,
                textbook_id=edge.textbook_id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                relation_type=edge.relation_type,
                description=edge.description,
            )
            for edge in graph.edges
        ],
    )


@router.get("/{textbook_id}", response_model=GraphDataResponse)
def get_graph(textbook_id: str) -> GraphDataResponse:
    try:
        textbook_service.get_textbook(textbook_id)
    except KeyError:
        raise AppError(message=f"Textbook '{textbook_id}' was not found.", code="textbook_not_found", status_code=404)
    nodes = graph_service.list_nodes(textbook_id)
    edges = graph_service.list_edges(textbook_id)
    return GraphDataResponse(
        textbook_id=textbook_id,
        nodes=[
            GraphNodeResponse(
                node_id=n.node_id,
                textbook_id=n.textbook_id,
                chapter_id=n.chapter_id,
                name=n.name,
                definition=n.definition,
                category=n.category,
                page=n.page,
                source_excerpt=n.source_excerpt,
                frequency=1,
            )
            for n in nodes
        ],
        edges=[
            GraphEdgeResponse(
                edge_id=e.edge_id,
                textbook_id=e.textbook_id,
                source_node_id=e.source_node_id,
                target_node_id=e.target_node_id,
                relation_type=e.relation_type,
                description=e.description,
            )
            for e in edges
        ],
    )
