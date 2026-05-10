from functools import lru_cache
from os import getenv
from pathlib import Path

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - exercised only without optional dependency
    BaseSettings = None
    SettingsConfigDict = None


class Settings(BaseSettings if BaseSettings is not None else BaseModel):
    app_name: str = Field(default="Knowledge Integration Agent")
    api_prefix: str = Field(default="/api")
    data_dir: str = Field(default="./data", alias="DATA_DIR")
    database_url: str = Field(default="sqlite:///./data/app.db", alias="DATABASE_URL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")
    llm_model: str = Field(default="", alias="LLM_MODEL")
    llm_enable_thinking: bool | None = Field(default=None, alias="LLM_ENABLE_THINKING")
    embedding_model: str = Field(default="", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


def _default_env_files() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[3]
    return [repo_root / ".env", repo_root / "backend" / ".env"]


def _read_env_file_values(paths: list[Path] | None = None) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in paths or _default_env_files():
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            values.setdefault(key, value)
    return values


def _resolve_setting(name: str, default: str, file_values: dict[str, str]) -> str:
    env_value = getenv(name)
    if env_value is not None and env_value.strip() != "":
        return env_value
    return file_values.get(name, default)


def _manual_settings_from_env() -> Settings:
    file_values = _read_env_file_values()
    llm_enable_thinking = _resolve_setting("LLM_ENABLE_THINKING", "", file_values)
    return Settings(
        DATA_DIR=_resolve_setting("DATA_DIR", "./data", file_values),
        DATABASE_URL=_resolve_setting("DATABASE_URL", "sqlite:///./data/app.db", file_values),
        OPENAI_API_KEY=_resolve_setting("OPENAI_API_KEY", "", file_values),
        OPENAI_BASE_URL=_resolve_setting("OPENAI_BASE_URL", "", file_values),
        LLM_MODEL=_resolve_setting("LLM_MODEL", "", file_values),
        LLM_ENABLE_THINKING=(
            llm_enable_thinking.strip().lower() in {"1", "true", "yes", "on"}
            if llm_enable_thinking is not None
            else None
        ),
        EMBEDDING_MODEL=_resolve_setting("EMBEDDING_MODEL", "", file_values),
        EMBEDDING_DIMENSION=int(_resolve_setting("EMBEDDING_DIMENSION", "1536", file_values)),
    )


@lru_cache
def get_settings() -> Settings:
    return _manual_settings_from_env()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
