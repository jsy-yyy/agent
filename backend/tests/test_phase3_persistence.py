from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.main import create_app
from app.services.chat_service import chat_service
from app.services.graph_service import graph_service
from app.services.integration_service import integration_service
from app.services.rag_service import rag_service
from app.services.task_service import task_service
from app.services.textbook_service import textbook_service
from app.storage.database import initialize_database, reset_database


def configure_database(monkeypatch, tmp_path: Path) -> Path:
    database_path = tmp_path / "phase3.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    clear_settings_cache()
    reset_database()
    return database_path


def seed_textbook() -> None:
    textbook_service.create_textbook(
        textbook_id="book_1",
        filename="physiology.txt",
        title="Physiology",
        file_format="txt",
        file_size=42,
        saved_path="data/uploads/physiology.txt",
        parse_status="parsed",
        total_pages=1,
        total_chars=120,
    )
    textbook_service.create_chapter(
        chapter_id="chapter_1",
        textbook_id="book_1",
        title="Chapter 1",
        order_index=1,
        page_start=1,
        page_end=2,
        content="Action potential depends on resting potential.",
    )


def test_database_startup_creates_schema_and_preserves_data(monkeypatch, tmp_path) -> None:
    database_path = configure_database(monkeypatch, tmp_path)

    assert database_path.exists()
    seed_textbook()

    initialize_database()

    textbook = textbook_service.get_textbook("book_1")
    assert textbook.title == "Physiology"
    assert textbook.file_format == "txt"


def test_textbook_and_chapter_persistence(monkeypatch, tmp_path) -> None:
    configure_database(monkeypatch, tmp_path)
    seed_textbook()

    textbooks = textbook_service.list_textbooks()
    chapters = textbook_service.list_chapters("book_1")

    assert [textbook.textbook_id for textbook in textbooks] == ["book_1"]
    assert len(chapters) == 1
    assert chapters[0].chapter_id == "chapter_1"
    assert chapters[0].char_count == len("Action potential depends on resting potential.")


def test_graph_nodes_edges_and_integration_decisions(monkeypatch, tmp_path) -> None:
    configure_database(monkeypatch, tmp_path)
    seed_textbook()
    graph_service.create_node(
        node_id="node_1",
        textbook_id="book_1",
        chapter_id="chapter_1",
        name="Action potential",
        definition="A rapid membrane potential reversal.",
        category="core_concept",
        page=1,
        source_excerpt="Action potential depends on resting potential.",
    )
    graph_service.create_node(
        node_id="node_2",
        textbook_id="book_1",
        chapter_id="chapter_1",
        name="Resting potential",
        definition="The baseline membrane potential.",
        category="core_concept",
        page=1,
        source_excerpt="resting potential",
    )
    graph_service.create_edge(
        edge_id="edge_1",
        textbook_id="book_1",
        source_node_id="node_2",
        target_node_id="node_1",
        relation_type="prerequisite",
        description="Resting potential is required first.",
    )
    integration_service.create_decision(
        decision_id="decision_1",
        action="merge",
        affected_node_ids=["node_1", "node_2"],
        result_node_id="merged_1",
        reason="Sample decision for persistence.",
        confidence=0.91,
    )
    updated = integration_service.update_decision_status("decision_1", "revised")

    assert len(graph_service.list_nodes("book_1")) == 2
    assert graph_service.list_edges("book_1")[0].relation_type == "prerequisite"
    assert updated.status == "revised"
    assert integration_service.get_decision("decision_1").affected_node_ids == ["node_1", "node_2"]


def test_rag_chunks_and_chat_history_survive_reinitialization(monkeypatch, tmp_path) -> None:
    configure_database(monkeypatch, tmp_path)
    seed_textbook()
    rag_service.create_chunk(
        chunk_id="chunk_1",
        textbook_id="book_1",
        chapter_id="chapter_1",
        chunk_index=0,
        text="Action potential source text.",
        page_start=1,
        page_end=1,
        token_count=8,
    )
    chat_service.create_session(session_id="session_1", title="Teacher feedback")
    chat_service.add_message(
        message_id="message_1",
        session_id="session_1",
        role="user",
        content="Please keep this concept.",
    )

    initialize_database()

    assert rag_service.list_chunks("book_1")[0].chunk_id == "chunk_1"
    assert chat_service.list_messages("session_1")[0].content == "Please keep this concept."


def test_task_persistence_survives_app_recreation(monkeypatch, tmp_path) -> None:
    configure_database(monkeypatch, tmp_path)
    client = TestClient(create_app())

    created = client.post("/api/tasks/simulated").json()
    task_id = created["task_id"]
    task_service.fail_task(task_id, "persisted failure")

    new_client = TestClient(create_app())
    response = new_client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["error_message"] == "persisted failure"
