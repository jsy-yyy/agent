from datetime import datetime

from app.models.records import RagChunkRecord
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect


class RagService:
    def create_chunk(
        self,
        *,
        chunk_id: str,
        textbook_id: str,
        chunk_index: int,
        text: str,
        chapter_id: str | None = None,
        page_start: int | None = None,
        page_end: int | None = None,
        token_count: int | None = None,
    ) -> RagChunkRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO rag_chunks (
                    chunk_id, textbook_id, chapter_id, chunk_index, text,
                    page_start, page_end, token_count, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    textbook_id,
                    chapter_id,
                    chunk_index,
                    text,
                    page_start,
                    page_end,
                    token_count,
                    to_storage_time(now),
                ),
            )
        return self.get_chunk(chunk_id)

    def get_chunk(self, chunk_id: str) -> RagChunkRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM rag_chunks WHERE chunk_id = ?",
                (chunk_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"RAG chunk '{chunk_id}' was not found.")
        return self._chunk_from_row(row)

    def list_chunks(self, textbook_id: str) -> list[RagChunkRecord]:
        with connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM rag_chunks
                WHERE textbook_id = ?
                ORDER BY chunk_index, chunk_id
                """,
                (textbook_id,),
            ).fetchall()
        return [self._chunk_from_row(row) for row in rows]

    @staticmethod
    def _chunk_from_row(row) -> RagChunkRecord:
        return RagChunkRecord(
            chunk_id=row["chunk_id"],
            textbook_id=row["textbook_id"],
            chapter_id=row["chapter_id"],
            chunk_index=row["chunk_index"],
            text=row["text"],
            page_start=row["page_start"],
            page_end=row["page_end"],
            token_count=row["token_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


rag_service = RagService()
