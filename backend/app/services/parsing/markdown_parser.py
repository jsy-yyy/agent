from pathlib import Path

from app.services.parsing.models import ParsedTextbook
from app.services.parsing.text_parser import split_text_by_headings


def parse_markdown(path: Path) -> ParsedTextbook:
    text = path.read_text(encoding="utf-8")
    chapters = split_text_by_headings(text, default_title=path.stem)
    return ParsedTextbook(
        total_pages=1,
        total_chars=sum(len(chapter.content) for chapter in chapters),
        chapters=chapters,
    )
