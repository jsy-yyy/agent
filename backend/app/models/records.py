from datetime import datetime

from pydantic import BaseModel

from app.core.task_status import TaskStatus


class TextbookRecord(BaseModel):
    textbook_id: str
    filename: str
    title: str
    file_format: str
    file_size: int
    saved_path: str
    parse_status: str
    total_pages: int
    total_chars: int
    created_at: datetime
    updated_at: datetime


class ChapterRecord(BaseModel):
    chapter_id: str
    textbook_id: str
    title: str
    order_index: int
    page_start: int | None = None
    page_end: int | None = None
    content: str
    char_count: int
    created_at: datetime


class GraphNodeRecord(BaseModel):
    node_id: str
    textbook_id: str
    chapter_id: str | None = None
    name: str
    definition: str
    category: str
    page: int | None = None
    source_excerpt: str
    created_at: datetime


class GraphEdgeRecord(BaseModel):
    edge_id: str
    textbook_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    description: str
    created_at: datetime


class IntegrationDecisionRecord(BaseModel):
    decision_id: str
    action: str
    affected_node_ids: list[str]
    result_node_id: str | None = None
    reason: str
    confidence: float
    status: str
    created_at: datetime
    updated_at: datetime


class MergedNodeRecord(BaseModel):
    merged_node_id: str
    name: str
    definition: str
    source_node_ids: list[str]
    created_at: datetime
    updated_at: datetime


class RagChunkRecord(BaseModel):
    chunk_id: str
    textbook_id: str
    chapter_id: str | None = None
    chunk_index: int
    text: str
    page_start: int | None = None
    page_end: int | None = None
    token_count: int | None = None
    created_at: datetime


class ChatSessionRecord(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessageRecord(BaseModel):
    message_id: str
    session_id: str
    role: str
    content: str
    created_at: datetime


class TaskRecord(BaseModel):
    task_id: str
    task_type: str
    status: TaskStatus
    progress: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
