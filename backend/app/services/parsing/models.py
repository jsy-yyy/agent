from pydantic import BaseModel


class ParsedChapter(BaseModel):
    title: str
    order_index: int
    content: str
    page_start: int | None = None
    page_end: int | None = None


class ParsedTextbook(BaseModel):
    total_pages: int
    total_chars: int
    chapters: list[ParsedChapter]
