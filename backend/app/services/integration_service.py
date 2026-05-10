import json
from datetime import datetime

from app.models.records import IntegrationDecisionRecord, MergedNodeRecord
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect


class IntegrationService:
    def create_decision(
        self,
        *,
        decision_id: str,
        action: str,
        affected_node_ids: list[str],
        reason: str,
        confidence: float,
        result_node_id: str | None = None,
        status: str = "active",
    ) -> IntegrationDecisionRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO integration_decisions (
                    decision_id, action, affected_node_ids, result_node_id,
                    reason, confidence, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    action,
                    json.dumps(affected_node_ids),
                    result_node_id,
                    reason,
                    confidence,
                    status,
                    to_storage_time(now),
                    to_storage_time(now),
                ),
            )
        return self.get_decision(decision_id)

    def get_decision(self, decision_id: str) -> IntegrationDecisionRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM integration_decisions WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Integration decision '{decision_id}' was not found.")
        return self._decision_from_row(row)

    def update_decision_status(self, decision_id: str, status: str) -> IntegrationDecisionRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                UPDATE integration_decisions
                SET status = ?, updated_at = ?
                WHERE decision_id = ?
                """,
                (status, to_storage_time(now), decision_id),
            )
        return self.get_decision(decision_id)

    def update_decision(
        self,
        decision_id: str,
        *,
        action: str | None = None,
        reason: str | None = None,
        status: str | None = None,
        confidence: float | None = None,
    ) -> IntegrationDecisionRecord:
        current = self.get_decision(decision_id)
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                UPDATE integration_decisions
                SET action = ?, reason = ?, status = ?, confidence = ?, updated_at = ?
                WHERE decision_id = ?
                """,
                (
                    action or current.action,
                    reason or current.reason,
                    status or current.status,
                    current.confidence if confidence is None else confidence,
                    to_storage_time(now),
                    decision_id,
                ),
            )
        return self.get_decision(decision_id)

    def list_decisions(self) -> list[IntegrationDecisionRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM integration_decisions ORDER BY created_at, decision_id"
            ).fetchall()
        return [self._decision_from_row(row) for row in rows]

    def clear_outputs(self) -> None:
        """Remove prior integration outputs before a fresh integration run."""
        with connect() as connection:
            connection.execute("DELETE FROM integration_decisions")
            connection.execute("DELETE FROM merged_nodes")

    def create_merged_node(
        self,
        *,
        merged_node_id: str,
        name: str,
        definition: str,
        source_node_ids: list[str],
    ) -> MergedNodeRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO merged_nodes (
                    merged_node_id, name, definition, source_node_ids,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    merged_node_id,
                    name,
                    definition,
                    json.dumps(source_node_ids),
                    to_storage_time(now),
                    to_storage_time(now),
                ),
            )
        return self.get_merged_node(merged_node_id)

    def get_merged_node(self, merged_node_id: str) -> MergedNodeRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM merged_nodes WHERE merged_node_id = ?",
                (merged_node_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Merged node '{merged_node_id}' was not found.")
        return MergedNodeRecord(
            merged_node_id=row["merged_node_id"],
            name=row["name"],
            definition=row["definition"],
            source_node_ids=json.loads(row["source_node_ids"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_merged_nodes(self) -> list[MergedNodeRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM merged_nodes ORDER BY created_at, merged_node_id"
            ).fetchall()
        return [
            MergedNodeRecord(
                merged_node_id=row["merged_node_id"],
                name=row["name"],
                definition=row["definition"],
                source_node_ids=json.loads(row["source_node_ids"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def list_merged_nodes(self) -> list[MergedNodeRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM merged_nodes ORDER BY created_at, merged_node_id"
            ).fetchall()
        return [
            MergedNodeRecord(
                merged_node_id=row["merged_node_id"],
                name=row["name"],
                definition=row["definition"],
                source_node_ids=json.loads(row["source_node_ids"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    @staticmethod
    def _decision_from_row(row) -> IntegrationDecisionRecord:
        return IntegrationDecisionRecord(
            decision_id=row["decision_id"],
            action=row["action"],
            affected_node_ids=json.loads(row["affected_node_ids"]),
            result_node_id=row["result_node_id"],
            reason=row["reason"],
            confidence=row["confidence"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


integration_service = IntegrationService()
