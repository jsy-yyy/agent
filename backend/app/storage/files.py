from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings

ALLOWED_TEXTBOOK_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}
FORMAT_BY_EXTENSION = {
    ".pdf": "pdf",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "txt",
}


def upload_directory() -> Path:
    path = Path(get_settings().data_dir) / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def textbook_format_for_filename(filename: str) -> str | None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_TEXTBOOK_EXTENSIONS:
        return None
    return FORMAT_BY_EXTENSION[extension]


async def save_upload_file(upload: UploadFile) -> tuple[Path, int]:
    original_name = Path(upload.filename or "textbook").name
    extension = Path(original_name).suffix.lower()
    safe_stem = Path(original_name).stem.replace(" ", "_") or "textbook"
    target_path = upload_directory() / f"{uuid4().hex}_{safe_stem}{extension}"
    size = 0
    with target_path.open("wb") as target:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            target.write(chunk)
    await upload.close()
    return target_path, size
