from pydantic import BaseModel, Field


# Relation types supported by the knowledge graph
VALID_RELATION_TYPES = {"prerequisite", "parallel", "contains", "applies_to"}


class GraphNodeRequest(BaseModel):
    name: str
    definition: str
    category: str
    page: int | None = None
    source_excerpt: str


class GraphNodeResponse(BaseModel):
    node_id: str
    textbook_id: str
    chapter_id: str | None = None
    name: str
    definition: str
    category: str
    page: int | None = None
    source_excerpt: str
    frequency: int = 1


class GraphEdgeResponse(BaseModel):
    edge_id: str
    textbook_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    description: str


class GraphDataResponse(BaseModel):
    textbook_id: str
    nodes: list[GraphNodeResponse] = Field(default_factory=list)
    edges: list[GraphEdgeResponse] = Field(default_factory=list)


class BuildGraphRequest(BaseModel):
    textbook_id: str


class BuildGraphResponse(BaseModel):
    textbook_id: str
    task_id: str
    status: str


class GraphSearchRequest(BaseModel):
    textbook_id: str
    query: str
    limit: int = Field(default=20, ge=1, le=100)


class GraphSearchResponse(BaseModel):
    query: str
    matched_nodes: list[GraphNodeResponse] = Field(default_factory=list)
    total_matches: int = 0
