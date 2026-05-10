from datetime import datetime

from app.models.records import ChatMessageRecord, ChatSessionRecord
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect


class ChatService:
    def create_session(self, *, session_id: str, title: str) -> ChatSessionRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO chat_sessions (session_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, title, to_storage_time(now), to_storage_time(now)),
            )
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> ChatSessionRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM chat_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Chat session '{session_id}' was not found.")
        return self._session_from_row(row)

    def add_message(
        self,
        *,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
    ) -> ChatMessageRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO chat_messages (message_id, session_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (message_id, session_id, role, content, to_storage_time(now)),
            )
            connection.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (to_storage_time(now), session_id),
            )
        return self.get_message(message_id)

    def get_message(self, message_id: str) -> ChatMessageRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM chat_messages WHERE message_id = ?",
                (message_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Chat message '{message_id}' was not found.")
        return self._message_from_row(row)

    def list_messages(self, session_id: str) -> list[ChatMessageRecord]:
        with connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at, message_id
                """,
                (session_id,),
            ).fetchall()
        return [self._message_from_row(row) for row in rows]

    @staticmethod
    def _session_from_row(row) -> ChatSessionRecord:
        return ChatSessionRecord(
            session_id=row["session_id"],
            title=row["title"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _message_from_row(row) -> ChatMessageRecord:
        return ChatMessageRecord(
            message_id=row["message_id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


chat_service = ChatService()
