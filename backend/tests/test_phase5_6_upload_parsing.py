from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.main import create_app
from app.storage.database import reset_database


def make_client(monkeypatch, tmp_path: Path) -> TestClient:
    data_dir = tmp_path / "data"
    database_path = data_dir / "app.db"
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    clear_settings_cache()
    reset_database()
    return TestClient(create_app())


def test_upload_accepts_multiple_textbook_files_and_lists_metadata(monkeypatch, tmp_path) -> None:
    client = make_client(monkeypatch, tmp_path)

    response = client.post(
        "/api/textbooks/upload",
        files=[
            ("files", ("intro.txt", b"Chapter 1\nText body", "text/plain")),
            ("files", ("notes.md", b"# First\nMarkdown body", "text/markdown")),
        ],
    )

    assert response.status_code == 201
    payload = response.json()
    assert len(payload["textbooks"]) == 2
    assert {item["file_format"] for item in payload["textbooks"]} == {"txt", "markdown"}

    list_response = client.get("/api/textbooks")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 2
    assert all(item["parse_status"] == "uploaded" for item in listed)


def test_unsupported_upload_returns_structured_error(monkeypatch, tmp_path) -> None:
    client = make_client(monkeypatch, tmp_path)

    response = client.post(
        "/api/textbooks/upload",
        files=[("files", ("archive.zip", b"not a textbook", "application/zip"))],
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_textbook_format"


def test_txt_parse_creates_chapter_and_completed_task(monkeypatch, tmp_path) -> None:
    client = make_client(monkeypatch, tmp_path)
    upload = client.post(
        "/api/textbooks/upload",
        files=[("files", ("intro.txt", "第一章 绪论\n内容一\n第二章 方法\n内容二".encode(), "text/plain"))],
    ).json()
    textbook_id = upload["textbooks"][0]["textbook_id"]

    parse_response = client.post(f"/api/textbooks/{textbook_id}/parse")

    assert parse_response.status_code == 200
    assert parse_response.json()["status"] == "completed"
    detail = client.get(f"/api/textbooks/{textbook_id}").json()
    assert detail["textbook_id"] == textbook_id
    assert detail["filename"] == "intro.txt"
    assert detail["title"] == "intro"
    assert detail["total_chars"] > 0
    assert [chapter["title"] for chapter in detail["chapters"]] == ["第一章 绪论", "第二章 方法"]


def test_markdown_parse_uses_headings(monkeypatch, tmp_path) -> None:
    client = make_client(monkeypatch, tmp_path)
    upload = client.post(
        "/api/textbooks/upload",
        files=[("files", ("notes.md", b"# Alpha\nA body\n## Beta\nB body", "text/markdown"))],
    ).json()
    textbook_id = upload["textbooks"][0]["textbook_id"]

    client.post(f"/api/textbooks/{textbook_id}/parse")
    detail = client.get(f"/api/textbooks/{textbook_id}").json()

    assert [chapter["title"] for chapter in detail["chapters"]] == ["Alpha", "Beta"]
    assert detail["chapters"][0]["char_count"] == len("A body")


def test_simple_pdf_parse_extracts_pages_and_fallback_chapter(monkeypatch, tmp_path) -> None:
    # Force the fallback path by blocking fitz import
    import builtins
    _orig_import = builtins.__import__

    def _block_fitz(name, *args, **kwargs):
        if name == "fitz":
            raise ModuleNotFoundError("fitz blocked for fallback test")
        return _orig_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _block_fitz)

    client = make_client(monkeypatch, tmp_path)
    pdf_bytes = b"%PDF-1.4\n1 0 obj << /Type /Page >> endobj\nBT (Chapter 1 PDF Text) ET\n%%EOF"
    upload = client.post(
        "/api/textbooks/upload",
        files=[("files", ("sample.pdf", pdf_bytes, "application/pdf"))],
    ).json()
    textbook_id = upload["textbooks"][0]["textbook_id"]

    parse_response = client.post(f"/api/textbooks/{textbook_id}/parse")

    assert parse_response.json()["status"] == "completed"
    detail = client.get(f"/api/textbooks/{textbook_id}").json()
    assert detail["total_pages"] >= 1
    assert "Chapter 1 PDF Text" in detail["chapters"][0]["content"]
