from datetime import datetime

from app.models.records import GraphEdgeRecord, GraphNodeRecord
from app.services.time import to_storage_time, utc_now
from app.storage.database import connect


class GraphService:
    def create_node(
        self,
        *,
        node_id: str,
        textbook_id: str,
        name: str,
        definition: str,
        category: str,
        source_excerpt: str,
        chapter_id: str | None = None,
        page: int | None = None,
    ) -> GraphNodeRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO graph_nodes (
                    node_id, textbook_id, chapter_id, name, definition,
                    category, page, source_excerpt, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    textbook_id,
                    chapter_id,
                    name,
                    definition,
                    category,
                    page,
                    source_excerpt,
                    to_storage_time(now),
                ),
            )
        return self.get_node(node_id)

    def get_node(self, node_id: str) -> GraphNodeRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM graph_nodes WHERE node_id = ?",
                (node_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Graph node '{node_id}' was not found.")
        return self._node_from_row(row)

    def list_nodes(self, textbook_id: str) -> list[GraphNodeRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM graph_nodes WHERE textbook_id = ? ORDER BY name, node_id",
                (textbook_id,),
            ).fetchall()
        return [self._node_from_row(row) for row in rows]

    def list_nodes_for_textbooks(self, textbook_ids: list[str]) -> list[GraphNodeRecord]:
        nodes: list[GraphNodeRecord] = []
        for textbook_id in textbook_ids:
            nodes.extend(self.list_nodes(textbook_id))
        return nodes

    def create_edge(
        self,
        *,
        edge_id: str,
        textbook_id: str,
        source_node_id: str,
        target_node_id: str,
        relation_type: str,
        description: str,
    ) -> GraphEdgeRecord:
        now = utc_now()
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO graph_edges (
                    edge_id, textbook_id, source_node_id, target_node_id,
                    relation_type, description, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge_id,
                    textbook_id,
                    source_node_id,
                    target_node_id,
                    relation_type,
                    description,
                    to_storage_time(now),
                ),
            )
        return self.get_edge(edge_id)

    def get_edge(self, edge_id: str) -> GraphEdgeRecord:
        with connect() as connection:
            row = connection.execute(
                "SELECT * FROM graph_edges WHERE edge_id = ?",
                (edge_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Graph edge '{edge_id}' was not found.")
        return self._edge_from_row(row)

    def list_edges(self, textbook_id: str) -> list[GraphEdgeRecord]:
        with connect() as connection:
            rows = connection.execute(
                "SELECT * FROM graph_edges WHERE textbook_id = ? ORDER BY edge_id",
                (textbook_id,),
            ).fetchall()
        return [self._edge_from_row(row) for row in rows]

    def list_edges_for_textbooks(self, textbook_ids: list[str]) -> list[GraphEdgeRecord]:
        edges: list[GraphEdgeRecord] = []
        for textbook_id in textbook_ids:
            edges.extend(self.list_edges(textbook_id))
        return edges

    @staticmethod
    def _node_from_row(row) -> GraphNodeRecord:
        return GraphNodeRecord(
            node_id=row["node_id"],
            textbook_id=row["textbook_id"],
            chapter_id=row["chapter_id"],
            name=row["name"],
            definition=row["definition"],
            category=row["category"],
            page=row["page"],
            source_excerpt=row["source_excerpt"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _edge_from_row(row) -> GraphEdgeRecord:
        return GraphEdgeRecord(
            edge_id=row["edge_id"],
            textbook_id=row["textbook_id"],
            source_node_id=row["source_node_id"],
            target_node_id=row["target_node_id"],
            relation_type=row["relation_type"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


graph_service = GraphService()
