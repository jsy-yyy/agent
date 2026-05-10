import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.core.config import get_settings
from app.storage.schema import SCHEMA_STATEMENTS


def sqlite_path_from_url(database_url: str) -> str:
    if database_url == "sqlite:///:memory:":
        return ":memory:"
    if database_url.startswith("sqlite:///"):
        return database_url.removeprefix("sqlite:///")
    raise ValueError("Only sqlite:/// database URLs are supported.")


def configured_database_path() -> str:
    return sqlite_path_from_url(get_settings().database_url)


@contextmanager
def connect(database_path: str | None = None) -> Iterator[sqlite3.Connection]:
    path = database_path or configured_database_path()
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database(database_path: str | None = None) -> None:
    with connect(database_path) as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)


def reset_database(database_path: str | None = None) -> None:
    path = database_path or configured_database_path()
    if path != ":memory:":
        db_file = Path(path)
        if db_file.exists():
            db_file.unlink()
    initialize_database(path)
