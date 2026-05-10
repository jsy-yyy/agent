import json
import uuid
from dataclasses import dataclass, field

from app.models.records import ChapterRecord
from app.prompts import prompts
from app.services.graph_service import GraphService, graph_service
from app.services.llm import LLMService


@dataclass
class ExtractionResult:
    textbook_id: str
    node_count: int = 0
    edge_count: int = 0
    failed_chapters: list[str] = field(default_factory=list)


class KnowledgeExtractor:
    def __init__(self, llm: LLMService, graph: GraphService = graph_service) -> None:
        self._llm = llm
        self._graph = graph

    def extract(self, textbook_id: str, chapters: list[ChapterRecord]) -> ExtractionResult:
        result = ExtractionResult(textbook_id=textbook_id)

        for chapter in chapters:
            try:
                chapter_nodes = self._extract_nodes(textbook_id, chapter)
                if not chapter_nodes:
                    continue
                result.node_count += len(chapter_nodes)

                chapter_edges = self._extract_relations(
                    textbook_id, chapter, chapter_nodes
                )
                result.edge_count += len(chapter_edges)
            except Exception:
                result.failed_chapters.append(chapter.chapter_id)

        return result

    def _extract_nodes(
        self, textbook_id: str, chapter: ChapterRecord
    ) -> dict[str, str]:
        """Call LLM to extract knowledge nodes. Returns {temp_id: real_db_node_id} mapping."""
        prompt = prompts.format("extraction.nodes", chapter_content=chapter.content)
        response = self._llm.generate_json(prompt, "extraction.nodes")
        nodes_data = response.get("nodes", [])
        if not isinstance(nodes_data, list):
            return {}

        id_map: dict[str, str] = {}
        for index, node in enumerate(nodes_data, start=1):
            temp_id = str(node.get("id", "")).strip() or f"node_{index:03d}"
            real_id = f"{textbook_id}_node_{uuid.uuid4().hex[:8]}"
            self._graph.create_node(
                node_id=real_id,
                textbook_id=textbook_id,
                chapter_id=chapter.chapter_id,
                name=str(node.get("name", "")),
                definition=str(node.get("definition", "")),
                category=str(node.get("category", "核心概念")),
                page=chapter.page_start,
                source_excerpt=str(node.get("source_excerpt", chapter.content[:200])),
            )
            id_map[temp_id] = real_id
        return id_map

    def _extract_relations(
        self, textbook_id: str, chapter: ChapterRecord, id_map: dict[str, str]
    ) -> list[str]:
        """Call LLM to extract edges. LLM uses temp IDs; we resolve to real DB IDs."""
        if len(id_map) < 2:
            return []

        nodes_for_prompt = []
        for temp_id, real_id in id_map.items():
            node = self._graph.get_node(real_id)
            nodes_for_prompt.append({
                "id": temp_id,
                "name": node.name,
                "definition": node.definition,
            })

        prompt = prompts.format(
            "extraction.relations",
            nodes_json=json.dumps(nodes_for_prompt, ensure_ascii=False),
            chapter_content=chapter.content,
        )
        response = self._llm.generate_json(prompt, "extraction.relations")
        edges_data = response.get("edges", [])
        if not isinstance(edges_data, list):
            return []

        edge_ids: list[str] = []
        temp_ids = list(id_map.keys())
        for edge in edges_data:
            src_temp = str(edge.get("source", ""))
            tgt_temp = str(edge.get("target", ""))
            if not src_temp and edge.get("source_node_index") is not None:
                try:
                    src_temp = temp_ids[int(edge["source_node_index"])]
                except (ValueError, TypeError, IndexError):
                    src_temp = ""
            if not tgt_temp and edge.get("target_node_index") is not None:
                try:
                    tgt_temp = temp_ids[int(edge["target_node_index"])]
                except (ValueError, TypeError, IndexError):
                    tgt_temp = ""
            if not src_temp or not tgt_temp:
                continue
            src_real = id_map.get(src_temp)
            tgt_real = id_map.get(tgt_temp)
            if not src_real or not tgt_real:
                continue

            relation_type = str(edge.get("relation_type", "parallel"))
            if relation_type not in {"prerequisite", "parallel", "contains", "applies_to"}:
                relation_type = "parallel"

            edge_id = f"{textbook_id}_edge_{uuid.uuid4().hex[:8]}"
            self._graph.create_edge(
                edge_id=edge_id,
                textbook_id=textbook_id,
                source_node_id=src_real,
                target_node_id=tgt_real,
                relation_type=relation_type,
                description=str(edge.get("description", "")),
            )
            edge_ids.append(edge_id)
        return edge_ids
