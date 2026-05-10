import re
import uuid
from dataclasses import dataclass

from app.models.records import GraphEdgeRecord, GraphNodeRecord
from app.prompts import prompts
from app.services.embedding.index_service import IndexService
from app.services.graph_service import graph_service
from app.services.integration_service import integration_service
from app.services.llm import LLMService
from app.services.textbook_service import textbook_service


COMPRESSION_TARGET_RATIO = 0.30


@dataclass
class IntegrationResult:
    merge_count: int = 0
    keep_count: int = 0
    remove_count: int = 0
    total_source_chars: int = 0
    integrated_chars: int = 0
    compression_ratio: float | None = None
    target_chars: int = 0
    target_met: bool = True


@dataclass
class IntegrationCandidate:
    action: str
    nodes: list[GraphNodeRecord]
    name: str
    definition: str
    reason: str
    confidence: float
    priority: float

    @property
    def char_count(self) -> int:
        return len(self.definition)

    @property
    def node_ids(self) -> list[str]:
        return [node.node_id for node in self.nodes]


def normalize_concept_name(name: str) -> str:
    """Normalize concept names for comparison: lowercase, strip spaces/punctuation."""
    name = name.strip().lower()
    name = re.sub(r"[（(].*?[）)]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


class IntegrationEngine:
    def __init__(self, llm: LLMService, index_service: IndexService) -> None:
        self._llm = llm
        self._index = index_service

    def integrate(self, textbook_ids: list[str]) -> IntegrationResult:
        """Run cross-textbook integration for the given textbooks."""
        if len(textbook_ids) < 2:
            raise ValueError("Need at least 2 textbooks for integration")

        integration_service.clear_outputs()
        all_nodes = graph_service.list_nodes_for_textbooks(textbook_ids)
        if not all_nodes:
            return IntegrationResult()

        total_chars = self._source_char_count(textbook_ids)
        if total_chars <= 0:
            total_chars = sum(len(n.definition) + len(n.source_excerpt) for n in all_nodes)

        normalized = {n.node_id: normalize_concept_name(n.name) for n in all_nodes}
        edges = graph_service.list_edges_for_textbooks(textbook_ids)
        degree = self._degree_by_node(edges)
        prerequisite_nodes = self._prerequisite_nodes(edges)

        node_texts = [f"{n.name}: {n.definition}" for n in all_nodes]
        node_ids = [n.node_id for n in all_nodes]
        self._index.build(node_ids, node_texts)

        candidates = self._build_candidates(all_nodes, normalized, degree, prerequisite_nodes)
        target_chars = max(int(total_chars * COMPRESSION_TARGET_RATIO), 0)
        kept_candidates, removed_candidates = self._select_within_target(candidates, target_chars)

        result = IntegrationResult(total_source_chars=total_chars, target_chars=target_chars)
        self._persist_kept_candidates(kept_candidates, result)
        self._persist_removed_candidates(removed_candidates, result)

        result.integrated_chars = sum(candidate.char_count for candidate in kept_candidates)
        result.compression_ratio = result.integrated_chars / total_chars if total_chars > 0 else None
        result.target_met = (
            result.compression_ratio is None
            or result.compression_ratio <= COMPRESSION_TARGET_RATIO
        )
        return result

    def _build_candidates(
        self,
        all_nodes: list[GraphNodeRecord],
        normalized: dict[str, str],
        degree: dict[str, int],
        prerequisite_nodes: set[str],
    ) -> list[IntegrationCandidate]:
        processed: set[str] = set()
        candidates: list[IntegrationCandidate] = []
        node_by_id = {node.node_id: node for node in all_nodes}
        query_texts = [f"{node.name}: {node.definition}" for node in all_nodes]
        if hasattr(self._index, "retrieve_many"):
            batched_similar = self._index.retrieve_many(query_texts, top_k=10)
        else:
            batched_similar = [self._index.retrieve(query, top_k=10) for query in query_texts]

        for node, similar in zip(all_nodes, batched_similar):
            if node.node_id in processed:
                continue
            group = [node]
            for sim_id, score in similar:
                if sim_id == node.node_id:
                    continue
                sim_node = node_by_id.get(sim_id)
                if not sim_node or sim_node.textbook_id == node.textbook_id or sim_node in group:
                    continue
                exact_match = normalized.get(sim_id) == normalized.get(node.node_id)
                if score > 0.86 or exact_match or (score > 0.72 and self._llm_review_equivalence(node, sim_node)):
                    group.append(sim_node)

            for grouped_node in group:
                processed.add(grouped_node.node_id)

            if len(group) >= 2:
                merged_name = max(group, key=lambda n: len(n.definition)).name
                merged_def = max(group, key=lambda n: len(n.definition)).definition
                candidates.append(
                    IntegrationCandidate(
                        action="merge",
                        nodes=group,
                        name=merged_name,
                        definition=merged_def,
                        reason=(
                            f"Merged {len(group)} equivalent concepts across textbooks "
                            f"into '{merged_name}'."
                        ),
                        confidence=0.88,
                        priority=self._priority(group, degree, prerequisite_nodes),
                    )
                )
            else:
                candidates.append(
                    IntegrationCandidate(
                        action="keep",
                        nodes=[node],
                        name=node.name,
                        definition=node.definition,
                        reason=f"Kept '{node.name}' because it is not redundant across textbooks.",
                        confidence=0.76,
                        priority=self._priority([node], degree, prerequisite_nodes),
                    )
                )

        return candidates

    def _persist_kept_candidates(
        self,
        candidates: list[IntegrationCandidate],
        result: IntegrationResult,
    ) -> None:
        for candidate in candidates:
            if candidate.action == "merge":
                merged_id = f"merged_{uuid.uuid4().hex[:8]}"
                integration_service.create_merged_node(
                    merged_node_id=merged_id,
                    name=candidate.name,
                    definition=candidate.definition,
                    source_node_ids=candidate.node_ids,
                )
                integration_service.create_decision(
                    decision_id=f"dec_{uuid.uuid4().hex[:8]}",
                    action="merge",
                    affected_node_ids=candidate.node_ids,
                    result_node_id=merged_id,
                    reason=candidate.reason,
                    confidence=candidate.confidence,
                    status="active",
                )
                result.merge_count += 1
            else:
                source_node = candidate.nodes[0]
                integration_service.create_decision(
                    decision_id=f"dec_{uuid.uuid4().hex[:8]}",
                    action="keep",
                    affected_node_ids=[source_node.node_id],
                    result_node_id=source_node.node_id,
                    reason=candidate.reason,
                    confidence=candidate.confidence,
                    status="active",
                )
                result.keep_count += 1

    @staticmethod
    def _persist_removed_candidates(
        candidates: list[IntegrationCandidate],
        result: IntegrationResult,
    ) -> None:
        for candidate in candidates:
            integration_service.create_decision(
                decision_id=f"dec_{uuid.uuid4().hex[:8]}",
                action="remove",
                affected_node_ids=candidate.node_ids,
                result_node_id=None,
                reason=(
                    f"Removed '{candidate.name}' to enforce the 30% compression target. "
                    "Lower priority content was excluded after preserving stronger shared "
                    "or prerequisite concepts."
                ),
                confidence=0.82,
                status="active",
            )
            result.remove_count += 1

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

    @staticmethod
    def _degree_by_node(edges: list[GraphEdgeRecord]) -> dict[str, int]:
        degree: dict[str, int] = {}
        for edge in edges:
            degree[edge.source_node_id] = degree.get(edge.source_node_id, 0) + 1
            degree[edge.target_node_id] = degree.get(edge.target_node_id, 0) + 1
        return degree

    @staticmethod
    def _prerequisite_nodes(edges: list[GraphEdgeRecord]) -> set[str]:
        node_ids: set[str] = set()
        for edge in edges:
            if edge.relation_type == "prerequisite":
                node_ids.add(edge.source_node_id)
                node_ids.add(edge.target_node_id)
        return node_ids

    @staticmethod
    def _priority(
        nodes: list[GraphNodeRecord],
        degree: dict[str, int],
        prerequisite_nodes: set[str],
    ) -> float:
        score = len(nodes) * 100.0
        for node in nodes:
            score += degree.get(node.node_id, 0) * 8
            if node.node_id in prerequisite_nodes:
                score += 25
            if any(token in node.category.lower() for token in ("核心", "概念", "principle", "core")):
                score += 10
            score += min(len(node.source_excerpt), 200) / 100
        return score

    @staticmethod
    def _select_within_target(
        candidates: list[IntegrationCandidate],
        target_chars: int,
    ) -> tuple[list[IntegrationCandidate], list[IntegrationCandidate]]:
        selected: list[IntegrationCandidate] = []
        removed: list[IntegrationCandidate] = []
        used_chars = 0
        ranked = sorted(
            candidates,
            key=lambda candidate: (candidate.priority, -max(candidate.char_count, 1)),
            reverse=True,
        )
        for candidate in ranked:
            if used_chars + candidate.char_count <= target_chars:
                selected.append(candidate)
                used_chars += candidate.char_count
            else:
                removed.append(candidate)
        return selected, removed

    def _llm_review_equivalence(self, node_a: GraphNodeRecord, node_b: GraphNodeRecord) -> bool:
        try:
            prompt = prompts.format(
                "alignment.concepts",
                textbook_a=node_a.textbook_id,
                name_a=node_a.name,
                definition_a=node_a.definition,
                textbook_b=node_b.textbook_id,
                name_b=node_b.name,
                definition_b=node_b.definition,
            )
            resp = self._llm.generate_json(prompt, "alignment.concepts")
            return bool(resp.get("are_equivalent", False))
        except Exception:
            return False
