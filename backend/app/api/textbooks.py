from fastapi import APIRouter, File, UploadFile

from app.models.records import ChapterRecord, TextbookRecord
from app.schemas.tasks import TaskResponse
from app.schemas.textbooks import (
    ChapterResponse,
    TextbookDetailResponse,
    TextbookResponse,
    UploadTextbooksResponse,
)
from app.services.textbook_service import textbook_service
from app.services.textbook_workflow import textbook_workflow

router = APIRouter(prefix="/api/textbooks", tags=["textbooks"])


@router.post("/upload", response_model=UploadTextbooksResponse, status_code=201)
async def upload_textbooks(files: list[UploadFile] = File(...)) -> UploadTextbooksResponse:
    uploaded = [await textbook_workflow.upload_textbook(file) for file in files]
    return UploadTextbooksResponse(textbooks=[to_textbook_response(item) for item in uploaded])


@router.get("", response_model=list[TextbookResponse])
def list_textbooks() -> list[TextbookResponse]:
    return [to_textbook_response(item) for item in textbook_service.list_textbooks()]


@router.get("/{textbook_id}", response_model=TextbookDetailResponse)
def get_textbook(textbook_id: str) -> TextbookDetailResponse:
    textbook, chapters = textbook_workflow.get_textbook_detail(textbook_id)
    return TextbookDetailResponse(
        textbook_id=textbook.textbook_id,
        filename=textbook.filename,
        title=textbook.title,
        total_pages=textbook.total_pages,
        total_chars=textbook.total_chars,
        chapters=[to_chapter_response(chapter) for chapter in chapters],
    )


@router.post("/{textbook_id}/parse", response_model=TaskResponse)
def parse_textbook(textbook_id: str) -> TaskResponse:
    return textbook_workflow.parse_textbook(textbook_id)


def to_textbook_response(record: TextbookRecord) -> TextbookResponse:
    return TextbookResponse(
        textbook_id=record.textbook_id,
        filename=record.filename,
        title=record.title,
        file_format=record.file_format,
        file_size=record.file_size,
        saved_path=record.saved_path,
        parse_status=record.parse_status,
        total_pages=record.total_pages,
        total_chars=record.total_chars,
    )


def to_chapter_response(record: ChapterRecord) -> ChapterResponse:
    return ChapterResponse(
        chapter_id=record.chapter_id,
        textbook_id=record.textbook_id,
        title=record.title,
        order_index=record.order_index,
        page_start=record.page_start,
        page_end=record.page_end,
        content=record.content,
        char_count=record.char_count,
    )
