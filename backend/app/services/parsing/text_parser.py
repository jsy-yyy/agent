from pathlib import Path

from app.services.parsing.chapter_headings import (
    clean_heading,
    infer_supplemental_titles_from_toc,
    is_heading_line,
)
from app.services.parsing.models import ParsedChapter, ParsedTextbook


def parse_txt(path: Path) -> ParsedTextbook:
    text = path.read_text(encoding="utf-8")
    chapters = split_text_by_headings(text, default_title=path.stem)
    return ParsedTextbook(
        total_pages=1,
        total_chars=sum(len(chapter.content) for chapter in chapters),
        chapters=chapters,
    )


def split_text_by_headings(text: str, *, default_title: str) -> list[ParsedChapter]:
    lines = text.splitlines()
    supplemental_titles = infer_supplemental_titles_from_toc(lines)
    heading_indexes = [
        index for index, line in enumerate(lines) if is_heading_line(line, supplemental_titles)
    ]
    if not heading_indexes:
        content = text.strip()
        return [
            ParsedChapter(
                title=default_title or "Untitled",
                order_index=1,
                content=content,
                page_start=1,
                page_end=1,
            )
        ]

    chapters_by_title: dict[str, ParsedChapter] = {}
    order_by_title: dict[str, int] = {}
    for order_index, start in enumerate(heading_indexes, start=1):
        end = heading_indexes[order_index] if order_index < len(heading_indexes) else len(lines)
        title = clean_heading(lines[start])
        body = "\n".join(lines[start + 1 : end]).strip()
        chapter = ParsedChapter(
            title=title,
            order_index=order_index,
            content=body,
            page_start=1,
            page_end=1,
        )
        order_by_title.setdefault(title, order_index)
        current = chapters_by_title.get(title)
        if current is None or len(chapter.content) > len(current.content):
            chapters_by_title[title] = chapter

    chapters = sorted(chapters_by_title.values(), key=lambda chapter: order_by_title[chapter.title])
    for order_index, chapter in enumerate(chapters, start=1):
        chapter.order_index = order_index
    return chapters
