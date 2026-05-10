from pydantic import BaseModel


class ChapterResponse(BaseModel):
    chapter_id: str
    textbook_id: str
    title: str
    order_index: int
    page_start: int | None = None
    page_end: int | None = None
    content: str
    char_count: int


class TextbookResponse(BaseModel):
    textbook_id: str
    filename: str
    title: str
    file_format: str
    file_size: int
    saved_path: str
    parse_status: str
    total_pages: int
    total_chars: int


class TextbookDetailResponse(BaseModel):
    textbook_id: str
    filename: str
    title: str
    total_pages: int
    total_chars: int
    chapters: list[ChapterResponse]


class UploadTextbooksResponse(BaseModel):
    textbooks: list[TextbookResponse]
