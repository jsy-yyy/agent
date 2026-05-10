from dataclasses import dataclass, field

from app.models.records import GraphEdgeRecord, GraphNodeRecord
from app.services.graph_service import graph_service
from app.services.integration_engine import COMPRESSION_TARGET_RATIO
from app.services.integration_service import integration_service
from app.services.textbook_service import textbook_service


@dataclass
class ProjectedGraphNode:
    node_id: str
    textbook_id: str
    name: str
    definition: str
    category: str
    source_excerpt: str
    chapter_id: str | None = None
    page: int | None = None
    frequency: int = 1


@dataclass
class ProjectedGraphEdge:
    edge_id: str
    textbook_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    description: str


@dataclass
class ProjectedGraph:
    nodes: list[ProjectedGraphNode] = field(default_factory=list)
    edges: list[ProjectedGraphEdge] = field(default_factory=list)


@dataclass
class IntegrationStats:
    total_decisions: int
    merge_count: int
    keep_count: int
    remove_count: int
    total_source_chars: int
    integrated_chars: int
    target_chars: int
    compression_ratio: float | None
    target_met: bool
    source_node_count: int
    source_edge_count: int
    integrated_node_count: int
    integrated_edge_count: int


class IntegrationProjectionService:
    def textbook_ids_for_stats(self) -> list[str]:
        return [
            textbook.textbook_id
            for textbook in textbook_service.list_textbooks()
            if textbook.parse_status == "parsed"
        ]

    def build_stats(self, textbook_ids: list[str] | None = None) -> IntegrationStats:
        ids = textbook_ids or self.textbook_ids_for_stats()
        decisions = [d for d in integration_service.list_decisions() if d.status == "active"]
        graph = self.build_merged_graph(ids)
        total_source_chars = self._source_char_count(ids)
        integrated_chars = self._integrated_char_count(ids)
        compression_ratio = (
            integrated_chars / total_source_chars
            if total_source_chars > 0
            else None
        )
        return IntegrationStats(
            total_decisions=len(decisions),
            merge_count=sum(1 for d in decisions if d.action == "merge"),
            keep_count=sum(1 for d in decisions if d.action == "keep"),
            remove_count=sum(1 for d in decisions if d.action == "remove"),
            total_source_chars=total_source_chars,
            integrated_chars=integrated_chars,
            target_chars=max(int(total_source_chars * COMPRESSION_TARGET_RATIO), 0),
            compression_ratio=compression_ratio,
            target_met=(
                compression_ratio is None
                or compression_ratio <= COMPRESSION_TARGET_RATIO
            ),
            source_node_count=len(graph_service.list_nodes_for_textbooks(ids)),
            source_edge_count=len(graph_service.list_edges_for_textbooks(ids)),
            integrated_node_count=len(graph.nodes),
            integrated_edge_count=len(graph.edges),
        )

    def build_merged_graph(self, textbook_ids: list[str] | None = None) -> ProjectedGraph:
        ids = textbook_ids or self.textbook_ids_for_stats()
        nodes_by_id = {
            node.node_id: node
            for node in graph_service.list_nodes_for_textbooks(ids)
        }
        node_map: dict[str, str] = {}
        projected_nodes: dict[str, ProjectedGraphNode] = {}

        for decision in integration_service.list_decisions():
            if decision.status != "active":
                continue
            if decision.action == "remove":
                continue
            if decision.action == "merge" and decision.result_node_id:
                try:
                    merged_node = integration_service.get_merged_node(decision.result_node_id)
                except KeyError:
                    continue
                projected_nodes[merged_node.merged_node_id] = ProjectedGraphNode(
                    node_id=merged_node.merged_node_id,
                    textbook_id="merged",
                    name=merged_node.name,
                    definition=merged_node.definition,
                    category="整合概念",
                    source_excerpt=f"来源节点: {', '.join(merged_node.source_node_ids)}",
                    frequency=len(merged_node.source_node_ids),
                )
                for source_node_id in decision.affected_node_ids:
                    node_map[source_node_id] = merged_node.merged_node_id
            elif decision.action == "keep":
                for source_node_id in decision.affected_node_ids:
                    source_node = nodes_by_id.get(source_node_id)
                    if source_node is None:
                        continue
                    node_map[source_node_id] = source_node.node_id
                    projected_nodes[source_node.node_id] = self._project_source_node(source_node)

        return ProjectedGraph(
            nodes=list(projected_nodes.values()),
            edges=self._project_edges(graph_service.list_edges_for_textbooks(ids), node_map),
        )

    def _integrated_char_count(self, textbook_ids: list[str]) -> int:
        total = 0
        nodes_by_id = {
            node.node_id: node
            for node in graph_service.list_nodes_for_textbooks(textbook_ids)
        }
        for decision in integration_service.list_decisions():
            if decision.status != "active" or decision.action == "remove":
                continue
            if decision.action == "merge" and decision.result_node_id:
                try:
                    total += len(integration_service.get_merged_node(decision.result_node_id).definition)
                except KeyError:
                    continue
            elif decision.action == "keep":
                for node_id in decision.affected_node_ids:
                    node = nodes_by_id.get(node_id)
                    if node is not None:
                        total += len(node.definition)
        return total

    @staticmethod
    def _project_source_node(node: GraphNodeRecord) -> ProjectedGraphNode:
        return ProjectedGraphNode(
            node_id=node.node_id,
            textbook_id=node.textbook_id,
            chapter_id=node.chapter_id,
            name=node.name,
            definition=node.definition,
            category=node.category,
            page=node.page,
            source_excerpt=node.source_excerpt,
            frequency=1,
        )

    @staticmethod
    def _project_edges(
        edges: list[GraphEdgeRecord],
        node_map: dict[str, str],
    ) -> list[ProjectedGraphEdge]:
        projected: list[ProjectedGraphEdge] = []
        seen: set[tuple[str, str, str, str]] = set()
        for edge in edges:
            source = node_map.get(edge.source_node_id)
            target = node_map.get(edge.target_node_id)
            if source is None or target is None or source == target:
                continue
            key = (source, target, edge.relation_type, edge.description)
            if key in seen:
                continue
            seen.add(key)
            projected.append(
                ProjectedGraphEdge(
                    edge_id=f"merged_{edge.edge_id}",
                    textbook_id="merged",
                    source_node_id=source,
                    target_node_id=target,
                    relation_type=edge.relation_type,
                    description=edge.description,
                )
            )
        return projected

    def _source_char_count(self, textbook_ids: list[str]) -> int:
        total = 0
        for textbook_id in textbook_ids:
            try:
                textbook = textbook_service.get_textbook(textbook_id)
            except KeyError:
                continue
            if textbook.total_chars > 0:
                total += textbook.total_chars
            else:
                total += sum(chapter.char_count for chapter in textbook_service.list_chapters(textbook_id))
        return total


integration_projection_service = IntegrationProjectionService()
