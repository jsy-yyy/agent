from datetime import datetime

from app.models.records import ChapterRecord, TextbookRecord
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect


class TextbookService:
    def create_textbook(
        self,
        *,
        textbook_id: str,
        filename: str,
        title: str,
        file_format: str,
        file_size: int,
        saved_path: str,
        parse_status: str = "pending",
        total_pages: int = 0,
        total_chars: int = 0,
    ) -> TextbookRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO textbooks (
                    textbook_id, filename, title, file_format, file_size, saved_path,
                    parse_status, total_pages, total_chars, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    textbook_id,
                    filename,
                    title,
                    file_format,
                    file_size,
                    saved_path,
                    parse_status,
                    total_pages,
                    total_chars,
                    to_storage_time(now),
                    to_storage_time(now),
                ),
            )
        return self.get_textbook(textbook_id)

    def get_textbook(self, textbook_id: str) -> TextbookRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM textbooks WHERE textbook_id = ?",
                (textbook_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Textbook '{textbook_id}' was not found.")
        return self._textbook_from_row(row)

    def list_textbooks(self) -> list[TextbookRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM textbooks ORDER BY created_at, textbook_id"
            ).fetchall()
        return [self._textbook_from_row(row) for row in rows]

    def update_parse_status(
        self,
        textbook_id: str,
        *,
        parse_status: str,
        total_pages: int | None = None,
        total_chars: int | None = None,
    ) -> TextbookRecord:
        current = self.get_textbook(textbook_id)
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                UPDATE textbooks
                SET parse_status = ?, total_pages = ?, total_chars = ?, updated_at = ?
                WHERE textbook_id = ?
                """,
                (
                    parse_status,
                    current.total_pages if total_pages is None else total_pages,
                    current.total_chars if total_chars is None else total_chars,
                    to_storage_time(now),
                    textbook_id,
                ),
            )
        return self.get_textbook(textbook_id)

    def replace_chapters(
        self,
        textbook_id: str,
        chapters: list[dict[str, object]],
    ) -> list[ChapterRecord]:
        with connect() as connection:
            connection.execute("DELETE FROM chapters WHERE textbook_id = ?", (textbook_id,))
        created = []
        for chapter in chapters:
            created.append(
                self.create_chapter(
                    chapter_id=str(chapter["chapter_id"]),
                    textbook_id=textbook_id,
                    title=str(chapter["title"]),
                    order_index=int(chapter["order_index"]),
                    page_start=chapter.get("page_start"),  # type: ignore[arg-type]
                    page_end=chapter.get("page_end"),  # type: ignore[arg-type]
                    content=str(chapter["content"]),
                )
            )
        return created

    def create_chapter(
        self,
        *,
        chapter_id: str,
        textbook_id: str,
        title: str,
        order_index: int,
        content: str,
        page_start: int | None = None,
        page_end: int | None = None,
    ) -> ChapterRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO chapters (
                    chapter_id, textbook_id, title, order_index, page_start,
                    page_end, content, char_count, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chapter_id,
                    textbook_id,
                    title,
                    order_index,
                    page_start,
                    page_end,
                    content,
                    len(content),
                    to_storage_time(now),
                ),
            )
        return self.get_chapter(chapter_id)

    def get_chapter(self, chapter_id: str) -> ChapterRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM chapters WHERE chapter_id = ?",
                (chapter_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Chapter '{chapter_id}' was not found.")
        return self._chapter_from_row(row)

    def list_chapters(self, textbook_id: str) -> list[ChapterRecord]:
        with connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chapters
                WHERE textbook_id = ?
                ORDER BY order_index, chapter_id
                """,
                (textbook_id,),
            ).fetchall()
        return [self._chapter_from_row(row) for row in rows]

    @staticmethod
    def _textbook_from_row(row) -> TextbookRecord:
        return TextbookRecord(
            textbook_id=row["textbook_id"],
            filename=row["filename"],
            title=row["title"],
            file_format=row["file_format"],
            file_size=row["file_size"],
            saved_path=row["saved_path"],
            parse_status=row["parse_status"],
            total_pages=row["total_pages"],
            total_chars=row["total_chars"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _chapter_from_row(row) -> ChapterRecord:
        return ChapterRecord(
            chapter_id=row["chapter_id"],
            textbook_id=row["textbook_id"],
            title=row["title"],
            order_index=row["order_index"],
            page_start=row["page_start"],
            page_end=row["page_end"],
            content=row["content"],
            char_count=row["char_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


textbook_service = TextbookService()
