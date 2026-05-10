"""Admin endpoints for data management."""

from pathlib import Path

from fastapi import APIRouter

from app.core.config import get_settings
from app.storage.database import connect, initialize_database

router = APIRouter(prefix="/api/admin")


@router.post("/reset")
def reset_all_data() -> dict:
    """Delete all data and reinitialize the database."""
    settings = get_settings()

    with connect() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
        conn.execute("PRAGMA foreign_keys = ON")

    # Clean up runtime data directories
    data_dir = Path(settings.data_dir)
    for subdir in ("uploads", "parsed", "graphs", "indexes", "reports"):
        dir_path = data_dir / subdir
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.name != ".gitkeep":
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)

    return {"status": "ok", "message": "All data has been cleared."}
