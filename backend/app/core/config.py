from functools import lru_cache
from os import getenv

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
    embedding_model: str = Field(default="", alias="EMBEDDING_MODEL")

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


def _manual_settings_from_env() -> Settings:
    return Settings(
        DATA_DIR=getenv("DATA_DIR", "./data"),
        DATABASE_URL=getenv("DATABASE_URL", "sqlite:///./data/app.db"),
        OPENAI_API_KEY=getenv("OPENAI_API_KEY", ""),
        OPENAI_BASE_URL=getenv("OPENAI_BASE_URL", ""),
        LLM_MODEL=getenv("LLM_MODEL", ""),
        EMBEDDING_MODEL=getenv("EMBEDDING_MODEL", ""),
    )


@lru_cache
def get_settings() -> Settings:
    if BaseSettings is None:
        return _manual_settings_from_env()
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
