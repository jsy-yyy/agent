from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, status

from app.core.errors import AppError
from app.core.task_status import TaskStatus
from app.models.records import ChapterRecord, TextbookRecord
from app.schemas.tasks import TaskResponse
from app.services.parsing.parser_service import parser_service
from app.services.task_service import task_service
from app.services.textbook_service import textbook_service
from app.storage.files import save_upload_file, textbook_format_for_filename


class TextbookWorkflow:
    async def upload_textbook(self, upload: UploadFile) -> TextbookRecord:
        filename = upload.filename or "textbook"
        file_format = textbook_format_for_filename(filename)
        if file_format is None:
            raise AppError(
                message="Unsupported textbook format. Use PDF, Markdown, or TXT.",
                code="unsupported_textbook_format",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        saved_path, file_size = await save_upload_file(upload)
        return textbook_service.create_textbook(
            textbook_id=f"book_{uuid4().hex}",
            filename=Path(filename).name,
            title=Path(filename).stem or Path(filename).name,
            file_format=file_format,
            file_size=file_size,
            saved_path=str(saved_path),
            parse_status="uploaded",
        )

    def parse_textbook(self, textbook_id: str) -> TaskResponse:
        textbook = self._get_textbook_or_error(textbook_id)
        task = task_service.create_task("parse_textbook", status=TaskStatus.RUNNING)
        textbook_service.update_parse_status(textbook_id, parse_status="parsing")

        try:
            parsed = parser_service.parse(Path(textbook.saved_path), textbook.file_format)
            chapter_payloads = [
                {
                    "chapter_id": f"chapter_{uuid4().hex}",
                    "title": chapter.title,
                    "order_index": chapter.order_index,
                    "page_start": chapter.page_start,
                    "page_end": chapter.page_end,
                    "content": chapter.content,
                }
                for chapter in parsed.chapters
            ]
            textbook_service.replace_chapters(textbook_id, chapter_payloads)
            textbook_service.update_parse_status(
                textbook_id,
                parse_status="parsed",
                total_pages=parsed.total_pages,
                total_chars=parsed.total_chars,
            )
            return task_service.update_task(
                task.task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
            )
        except Exception as exc:
            textbook_service.update_parse_status(textbook_id, parse_status="failed")
            return task_service.update_task(
                task.task_id,
                status=TaskStatus.FAILED,
                progress=0,
                error_message=str(exc),
            )

    def get_textbook_detail(self, textbook_id: str) -> tuple[TextbookRecord, list[ChapterRecord]]:
        textbook = self._get_textbook_or_error(textbook_id)
        return textbook, textbook_service.list_chapters(textbook_id)

    def _get_textbook_or_error(self, textbook_id: str) -> TextbookRecord:
        try:
            return textbook_service.get_textbook(textbook_id)
        except KeyError:
            raise AppError(
                message=f"Textbook '{textbook_id}' was not found.",
                code="textbook_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            ) from None


textbook_workflow = TextbookWorkflow()
