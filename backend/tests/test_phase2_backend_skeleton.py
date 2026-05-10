from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.main import create_app
from app.services.task_service import task_service


def make_client() -> TestClient:
    task_service.reset()
    return TestClient(create_app())


def test_health_returns_status_and_env_override(monkeypatch) -> None:
    monkeypatch.setenv("DATA_DIR", "/tmp/custom-data")
    clear_settings_cache()

    client = make_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "Knowledge Integration Agent",
    }
    assert clear_settings_cache() is None


def test_settings_read_environment_overrides(monkeypatch) -> None:
    from app.core.config import get_settings

    monkeypatch.setenv("DATA_DIR", "/tmp/phase2-data")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/phase2.db")
    clear_settings_cache()

    settings = get_settings()

    assert settings.data_dir == "/tmp/phase2-data"
    assert settings.database_url == "sqlite:///tmp/phase2.db"
    clear_settings_cache()


def test_settings_can_read_repo_env_file_independent_of_cwd(monkeypatch, tmp_path) -> None:
    from app.core.config import get_settings

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=test-key",
                "LLM_MODEL=test-llm",
                "EMBEDDING_MODEL=test-embedding",
                "EMBEDDING_DIMENSION=1024",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("EMBEDDING_DIMENSION", raising=False)
    monkeypatch.setattr("app.core.config._default_env_files", lambda: [env_file])
    clear_settings_cache()

    settings = get_settings()

    assert settings.openai_api_key == "test-key"
    assert settings.llm_model == "test-llm"
    assert settings.embedding_model == "test-embedding"
    assert settings.embedding_dimension == 1024
    clear_settings_cache()


def test_empty_environment_variables_do_not_override_env_file(monkeypatch, tmp_path) -> None:
    from app.core.config import get_settings

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LLM_MODEL=file-llm",
                "EMBEDDING_MODEL=file-embedding",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LLM_MODEL", "")
    monkeypatch.setenv("EMBEDDING_MODEL", "")
    monkeypatch.setattr("app.core.config._default_env_files", lambda: [env_file])
    clear_settings_cache()

    settings = get_settings()

    assert settings.llm_model == "file-llm"
    assert settings.embedding_model == "file-embedding"
    clear_settings_cache()


def test_simulated_task_can_be_created_read_and_failed() -> None:
    client = make_client()

    create_response = client.post("/api/tasks/simulated")
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["task_type"] == "simulated"
    assert created["status"] == "pending"
    assert created["progress"] == 0

    task_id = created["task_id"]
    read_response = client.get(f"/api/tasks/{task_id}")
    assert read_response.status_code == 200
    assert read_response.json()["task_id"] == task_id

    fail_response = client.post(
        f"/api/tasks/{task_id}/fail",
        json={"error_message": "simulated failure"},
    )
    assert fail_response.status_code == 200
    failed = fail_response.json()
    assert failed["status"] == "failed"
    assert failed["error_message"] == "simulated failure"


def test_application_errors_use_consistent_shape() -> None:
    client = make_client()

    response = client.get("/api/tasks/missing-task")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "task_not_found",
            "message": "Task 'missing-task' was not found.",
        }
    }


def test_validation_errors_use_consistent_shape() -> None:
    client = make_client()
    created = client.post("/api/tasks/simulated").json()

    response = client.post(
        f"/api/tasks/{created['task_id']}/fail",
        json={"error_message": ""},
    )

    payload = response.json()
    assert response.status_code == 422
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed."
