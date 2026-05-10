from datetime import datetime

import pytest

from app.models.records import ChapterRecord
from app.services.graph_service import graph_service
from app.services.knowledge_extractor import ExtractionResult, KnowledgeExtractor
from app.services.llm import LLMProviderError
from app.services.llm.service import LLMService
from app.services.textbook_service import textbook_service
from app.storage.database import connect, initialize_database


class FakeLLMProvider:
    def __init__(self, node_response: dict | None = None, edge_response: dict | None = None) -> None:
        self.node_response = node_response or {
            "nodes": [
                {"id": "node_001", "name": "动作电位", "definition": "膜电位快速倒转", "category": "核心概念"},
                {"id": "node_002", "name": "静息电位", "definition": "细胞未受刺激时的膜电位", "category": "核心概念"},
            ]
        }
        self.edge_response = edge_response or {
            "edges": [
                {
                    "source": "node_001",
                    "target": "node_002",
                    "relation_type": "prerequisite",
                    "description": "理解动作电位需要先掌握静息电位",
                }
            ]
        }

    def generate_text(self, prompt: str) -> str:
        return "text response"

    def generate_json(self, prompt: str, schema_name: str) -> dict:
        if schema_name == "extraction.nodes":
            return self.node_response
        return self.edge_response


def _make_chapter(chapter_id: str, content: str = "样本章节内容") -> ChapterRecord:
    return ChapterRecord(
        chapter_id=chapter_id,
        textbook_id="tb1",
        title="第一章",
        order_index=0,
        page_start=1,
        page_end=10,
        content=content,
        char_count=len(content),
        created_at=datetime(2024, 1, 1),
    )


def _seed_textbook(textbook_id: str = "tb1", chapter_id: str = "ch1") -> None:
    try:
        textbook_service.get_textbook(textbook_id)
    except KeyError:
        textbook_service.create_textbook(
            textbook_id=textbook_id, filename="test.txt", title=f"Test {textbook_id}",
            file_format="txt", file_size=100, saved_path="/tmp/test.txt",
        )
    textbook_service.replace_chapters(
        textbook_id=textbook_id,
        chapters=[{"chapter_id": chapter_id, "title": "第一章", "order_index": 0, "page_start": 1, "page_end": 10, "content": "样本章节内容", "char_count": 6}],
    )


@pytest.fixture(autouse=True)
def reset_database() -> None:
    from app.storage.database import reset_database as db_reset
    db_reset()


class TestKnowledgeExtractor:
    def test_extracts_nodes_from_chapter(self) -> None:
        _seed_textbook("tb1")
        fake = FakeLLMProvider()
        llm = LLMService(fake)
        extractor = KnowledgeExtractor(llm, graph_service)
        chapter = _make_chapter("ch1")

        result = extractor.extract("tb1", [chapter])

        assert result.node_count == 2
        assert result.edge_count == 1
        assert result.failed_chapters == []

        nodes = graph_service.list_nodes("tb1")
        assert len(nodes) == 2
        assert nodes[0].name in ("动作电位", "静息电位")

        edges = graph_service.list_edges("tb1")
        assert len(edges) == 1
        assert edges[0].relation_type == "prerequisite"

    def test_isolates_chapter_extraction_failure(self) -> None:
        _seed_textbook("tb1")

        class BadProvider:
            def generate_text(self, prompt: str) -> str:
                return ""
            def generate_json(self, prompt: str, schema_name: str) -> dict:
                raise LLMProviderError("extraction failed")

        llm = LLMService(BadProvider())
        extractor = KnowledgeExtractor(llm, graph_service)
        good_chapter = _make_chapter("ch1")
        bad_chapter = _make_chapter("ch2")

        result = extractor.extract("tb1", [good_chapter, bad_chapter])

        assert result.node_count == 0
        assert result.edge_count == 0
        assert len(result.failed_chapters) == 2

    def test_empty_nodes_response_skips_chapter(self) -> None:
        _seed_textbook("tb1")
        fake = FakeLLMProvider(node_response={"nodes": []})
        llm = LLMService(fake)
        extractor = KnowledgeExtractor(llm, graph_service)

        result = extractor.extract("tb1", [_make_chapter("ch1")])

        assert result.node_count == 0
        assert result.edge_count == 0

    def test_no_edges_when_only_one_node(self) -> None:
        _seed_textbook("tb1")
        fake = FakeLLMProvider(node_response={"nodes": [{"id": "node_001", "name": "概念A", "definition": "定义", "category": "核心概念"}]})
        llm = LLMService(fake)
        extractor = KnowledgeExtractor(llm, graph_service)

        result = extractor.extract("tb1", [_make_chapter("ch1")])

        assert result.node_count == 1
        assert result.edge_count == 0

    def test_extraction_result_dataclass_defaults(self) -> None:
        result = ExtractionResult(textbook_id="tb1")
        assert result.node_count == 0
        assert result.edge_count == 0
        assert result.failed_chapters == []

    def test_preserves_chapter_and_textbook_provenance(self) -> None:
        _seed_textbook("tb_provenance", chapter_id="ch_provenance")
        fake = FakeLLMProvider()
        llm = LLMService(fake)
        extractor = KnowledgeExtractor(llm, graph_service)
        chapter = _make_chapter("ch_provenance", "具体内容")

        extractor.extract("tb_provenance", [chapter])

        nodes = graph_service.list_nodes("tb_provenance")
        assert len(nodes) > 0
        for node in nodes:
            assert node.textbook_id == "tb_provenance"

    def test_invalid_edge_references_are_skipped(self) -> None:
        _seed_textbook("tb1")
        fake = FakeLLMProvider(edge_response={
            "edges": [
                {"source": "node_001", "target": "node_099", "relation_type": "parallel", "description": "bad edge - nonexistent target"},
                {"source": "node_001", "target": "node_002", "relation_type": "contains", "description": "good edge"},
            ]
        })
        llm = LLMService(fake)
        extractor = KnowledgeExtractor(llm, graph_service)

        result = extractor.extract("tb1", [_make_chapter("ch1")])

        assert result.edge_count == 1
        edges = graph_service.list_edges("tb1")
        assert edges[0].description == "good edge"


class TestGraphApiEndpoints:
    def test_get_graph_returns_empty_for_unprocessed_textbook(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient

        _seed_textbook("tb_empty")

        client = TestClient(app)
        response = client.get("/api/graph/tb_empty")
        assert response.status_code == 200
        data = response.json()
        assert data["textbook_id"] == "tb_empty"
        assert data["nodes"] == []
        assert data["edges"] == []

    def test_get_graph_raises_for_unknown_textbook(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/graph/nonexistent")
        assert response.status_code == 404

    def test_build_graph_requires_chapters(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient

        # Create textbook without chapters
        try:
            textbook_service.get_textbook("tb_noch")
        except KeyError:
            textbook_service.create_textbook(
                textbook_id="tb_noch", filename="test.txt", title="Test",
                file_format="txt", file_size=100, saved_path="/tmp/test.txt",
            )

        client = TestClient(app)
        response = client.post("/api/graph/build", json={"textbook_id": "tb_noch"})
        assert response.status_code == 400
        assert "no_chapters" in response.json()["error"]["code"]
