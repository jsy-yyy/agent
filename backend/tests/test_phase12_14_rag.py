import pytest

from app.services.rag_pipeline import RagPipeline, chunk_text


class TestChunkText:
    def test_empty_text_returns_empty(self) -> None:
        assert chunk_text("") == []

    def test_short_text_returns_single_chunk(self) -> None:
        chunks = chunk_text("hello", chunk_size=600)
        assert len(chunks) == 1
        assert chunks[0] == "hello"

    def test_long_text_splits_into_multiple(self) -> None:
        text = "A" * 1200
        chunks = chunk_text(text, chunk_size=600, overlap=80)
        assert len(chunks) >= 2

    def test_overlap_preserves_context(self) -> None:
        text = "ABCDEFGHIJ"
        chunks = chunk_text(text, chunk_size=5, overlap=2)
        # First: ABCDE, second starts at position 3: CDEFG, third: FGHIJ
        assert chunks[0] == "ABCDE"
        assert chunks[1][:2] == chunks[0][-2:]


class FakeLLM:
    def generate_text(self, prompt: str) -> str:
        return "基于提供的教材内容，答案是测试回复。"
    def generate_json(self, prompt: str, schema_name: str) -> dict:
        return {}


class FakeIndex:
    def __init__(self) -> None:
        self.is_loaded = True
        self.size = 0
    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        self.size = len(chunk_ids)
    def retrieve(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        return []


class TestRagPipeline:
    def test_answer_without_index_returns_not_found(self) -> None:
        llm = FakeLLM()
        index = FakeIndex()
        pipeline = RagPipeline(llm, index)
        result = pipeline.answer("测试问题")
        assert "当前知识库中未找到相关信息" in result["answer"]
        assert result["citations"] == []


class TestRagApiEndpoints:
    def test_index_needs_chapters(self) -> None:
        from app.main import app
        from app.services.textbook_service import textbook_service
        from app.storage.database import reset_database as db_reset
        from fastapi.testclient import TestClient

        db_reset()
        textbook_service.create_textbook(
            textbook_id="tb_rag", filename="test.txt", title="Test", file_format="txt",
            file_size=100, saved_path="/tmp/test.txt",
        )

        client = TestClient(app)
        response = client.post("/api/rag/index", json={"textbook_id": "tb_rag"})
        assert response.status_code == 400
        assert "no_chapters" in response.json()["error"]["code"]

    def test_query_without_index_fails(self) -> None:
        from app.main import app
        from app.storage.database import reset_database as db_reset
        from fastapi.testclient import TestClient

        db_reset()
        client = TestClient(app)
        response = client.post("/api/rag/query", json={"question": "test"})
        assert response.status_code == 400
        assert "index_not_built" in response.json()["error"]["code"]

    def test_status_endpoint(self) -> None:
        from app.main import app
        from app.storage.database import reset_database as db_reset
        from fastapi.testclient import TestClient

        db_reset()
        client = TestClient(app)
        response = client.get("/api/rag/status")
        assert response.status_code == 200
        data = response.json()
        assert "indexed_chunks" in data
