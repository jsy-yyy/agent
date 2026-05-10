import pytest

from app.core.config import clear_settings_cache
from app.services.embedding import EmbeddingProviderError
from app.services.integration_engine import IntegrationEngine, normalize_concept_name
from app.services.integration_projection import integration_projection_service
from app.services.integration_service import integration_service
from app.services.graph_service import graph_service
from app.services.textbook_service import textbook_service
from app.storage.database import reset_database


class TestNormalizeConceptName:
    def test_strips_spaces(self) -> None:
        assert normalize_concept_name("  动作电位  ") == "动作电位"

    def test_lowercases(self) -> None:
        assert normalize_concept_name("Action Potential") == "action potential"

    def test_removes_parenthetical(self) -> None:
        assert normalize_concept_name("动作电位(action potential)") == "动作电位"


class FakeLLMProvider:
    def generate_text(self, prompt: str) -> str:
        return ""
    def generate_json(self, prompt: str, schema_name: str) -> dict:
        return {"are_equivalent": False, "confidence": 0.5, "reason": "different"}


class FakeIndexService:
    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        self._ids = chunk_ids
    def retrieve(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        return [(i, 0.5) for i in self._ids[:top_k] if i != (self._ids[0] if self._ids else None)]


class SimilarityIndexService:
    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        self._ids = chunk_ids

    def retrieve(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        if "Shared" in query:
            return [("n1", 1.0), ("n2", 0.92)]
        return []

    def retrieve_many(self, queries: list[str], top_k: int = 5) -> list[list[tuple[str, float]]]:
        return [self.retrieve(query, top_k=top_k) for query in queries]


class RateLimitedIndexService:
    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        self._ids = chunk_ids

    def retrieve_many(self, queries: list[str], top_k: int = 5) -> list[list[tuple[str, float]]]:
        raise EmbeddingProviderError("Error code: 429 - rate limit")


def configure_database(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "integration.db"
    data_dir = tmp_path / "data"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    clear_settings_cache()
    reset_database()


def seed_integration_graph() -> None:
    textbook_service.create_textbook(
        textbook_id="tb1",
        filename="a.txt",
        title="A",
        file_format="txt",
        file_size=1,
        saved_path="a.txt",
        parse_status="parsed",
        total_chars=50,
    )
    textbook_service.create_textbook(
        textbook_id="tb2",
        filename="b.txt",
        title="B",
        file_format="txt",
        file_size=1,
        saved_path="b.txt",
        parse_status="parsed",
        total_chars=50,
    )
    graph_service.create_node(
        node_id="n1",
        textbook_id="tb1",
        name="Shared",
        definition="A" * 20,
        category="核心概念",
        source_excerpt="source",
    )
    graph_service.create_node(
        node_id="n2",
        textbook_id="tb2",
        name="Shared",
        definition="B" * 25,
        category="核心概念",
        source_excerpt="source",
    )
    graph_service.create_node(
        node_id="n3",
        textbook_id="tb1",
        name="Optional",
        definition="C" * 20,
        category="补充概念",
        source_excerpt="source",
    )


class TestIntegrationEngine:
    def test_requires_at_least_two_textbooks(self) -> None:
        from app.services.llm import LLMService
        engine = IntegrationEngine(LLMService(FakeLLMProvider()), FakeIndexService())
        with pytest.raises(ValueError, match="Need at least 2"):
            engine.integrate(["tb1"])

    def test_empty_ids_raises_value_error(self) -> None:
        from app.services.llm import LLMService
        engine = IntegrationEngine(LLMService(FakeLLMProvider()), FakeIndexService())
        with pytest.raises(ValueError, match="at least 2"):
            engine.integrate([])

    def test_enforces_30_percent_target_and_creates_remove_decision(self, monkeypatch, tmp_path) -> None:
        from app.services.llm import LLMService

        configure_database(monkeypatch, tmp_path)
        seed_integration_graph()
        engine = IntegrationEngine(LLMService(FakeLLMProvider()), SimilarityIndexService())

        result = engine.integrate(["tb1", "tb2"])

        assert result.target_chars == 30
        assert result.integrated_chars == 25
        assert result.compression_ratio == 0.25
        assert result.target_met is True
        assert result.merge_count == 1
        assert result.remove_count == 1

        decisions = integration_service.list_decisions()
        assert {decision.action for decision in decisions} == {"merge", "remove"}
        remove = next(decision for decision in decisions if decision.action == "remove")
        assert remove.affected_node_ids == ["n3"]

    def test_stats_and_merged_graph_use_active_decisions(self, monkeypatch, tmp_path) -> None:
        from app.services.llm import LLMService

        configure_database(monkeypatch, tmp_path)
        seed_integration_graph()
        engine = IntegrationEngine(LLMService(FakeLLMProvider()), SimilarityIndexService())
        engine.integrate(["tb1", "tb2"])

        stats = integration_projection_service.build_stats(["tb1", "tb2"])
        graph = integration_projection_service.build_merged_graph(["tb1", "tb2"])

        assert stats.total_source_chars == 100
        assert stats.integrated_chars == 25
        assert stats.compression_ratio == 0.25
        assert stats.integrated_node_count == 1
        assert graph.nodes[0].frequency == 2
        assert [node.node_id for node in graph.nodes] == [
            decision.result_node_id
            for decision in integration_service.list_decisions()
            if decision.action == "merge"
        ]


class TestIntegrationApiEndpoints:
    def test_list_decisions_returns_empty_when_none(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient
        from app.storage.database import reset_database as db_reset

        db_reset()
        client = TestClient(app)
        response = client.get("/api/integration/decisions")
        assert response.status_code == 200
        assert response.json()["decisions"] == []

    def test_run_integration_needs_two_textbooks(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient
        from app.storage.database import reset_database as db_reset

        db_reset()
        client = TestClient(app)
        response = client.post("/api/integration/run")
        assert response.status_code == 400
        assert "insufficient_textbooks" in response.json()["error"]["code"]

    def test_get_stats(self) -> None:
        from app.main import app
        from fastapi.testclient import TestClient
        from app.storage.database import reset_database as db_reset

        db_reset()
        client = TestClient(app)
        response = client.get("/api/integration/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_decisions"] == 0

    def test_merged_graph_and_report_endpoints_are_consistent(self, monkeypatch, tmp_path) -> None:
        from app.main import create_app
        from app.services.llm import LLMService
        from fastapi.testclient import TestClient

        configure_database(monkeypatch, tmp_path)
        seed_integration_graph()
        engine = IntegrationEngine(LLMService(FakeLLMProvider()), SimilarityIndexService())
        engine.integrate(["tb1", "tb2"])

        client = TestClient(create_app())
        graph_response = client.get("/api/graph/merged")
        assert graph_response.status_code == 200
        graph_data = graph_response.json()
        assert graph_data["textbook_id"] == "merged"
        assert len(graph_data["nodes"]) == 1
        assert graph_data["nodes"][0]["frequency"] == 2

        report_response = client.post("/api/report/generate")
        assert report_response.status_code == 200
        content_response = client.get("/api/report")
        content = content_response.json()["content"]
        assert "- 原始字符数: 100" in content
        assert "- 整合后字符数: 25" in content
        assert "- 压缩比: 25.00%" in content

    def test_run_integration_returns_structured_error_on_embedding_rate_limit(self, monkeypatch, tmp_path) -> None:
        from app.main import create_app
        from app.services.llm import LLMService
        from fastapi.testclient import TestClient

        configure_database(monkeypatch, tmp_path)
        seed_integration_graph()

        app = create_app()
        app.state.llm_service = LLMService(FakeLLMProvider())
        app.state.index_service = RateLimitedIndexService()

        client = TestClient(app)
        response = client.post("/api/integration/run")

        assert response.status_code == 429
        payload = response.json()
        assert payload["error"]["code"] == "embedding_unavailable"
        assert "Embedding request failed during integration" in payload["error"]["message"]
