import re

PRIMARY_CHAPTER_PATTERN = re.compile(
    r"^(第\s*[一二三四五六七八九十百千\d]+\s*章(?:\s*.+)?|Chapter\s+\d+.*|绪\s*论)$",
    re.I,
)
MARKDOWN_HEADING_PATTERN = re.compile(r"^#{1,3}\s+.+$")
TOC_MARKER_PATTERN = re.compile(r"^(目录|contents?)$", re.I)
TOC_ENTRY_PATTERN = re.compile(
    r"^(?P<title>.+?)(?:\.{2,}|·{2,}|\s{2,}|\t+|\s+)\s*(?P<page>\d{1,4})\s*$"
)


def clean_heading(line: str) -> str:
    return line.strip().lstrip("#").strip()


def looks_like_toc_entry(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    match = TOC_ENTRY_PATTERN.match(stripped)
    if not match:
        return False
    title = clean_heading(match.group("title"))
    return bool(title) and len(title) <= 40


def _extract_toc_title(line: str) -> str | None:
    match = TOC_ENTRY_PATTERN.match(line.strip())
    if not match:
        return None
    title = clean_heading(match.group("title"))
    if not title or len(title) > 40:
        return None
    return title


def infer_supplemental_titles_from_toc(lines: list[str]) -> set[str]:
    marker_index = next(
        (index for index, line in enumerate(lines) if TOC_MARKER_PATTERN.match(clean_heading(line))),
        None,
    )
    if marker_index is None:
        return set()

    toc_candidates: list[str] = []
    empty_streak = 0
    window_end = min(len(lines), marker_index + 80)

    for raw_line in lines[marker_index + 1 : window_end]:
        stripped = raw_line.strip()
        if not stripped:
            empty_streak += 1
            if toc_candidates and empty_streak >= 2:
                break
            continue

        empty_streak = 0
        title = _extract_toc_title(stripped)
        if title:
            toc_candidates.append(title)

    if not any(PRIMARY_CHAPTER_PATTERN.match(title) for title in toc_candidates):
        return set()

    supplemental_titles: set[str] = set()
    for title in toc_candidates:
        if PRIMARY_CHAPTER_PATTERN.match(title):
            continue
        if _appears_as_standalone_title(lines, title):
            supplemental_titles.add(title)
    return supplemental_titles


def _appears_as_standalone_title(lines: list[str], title: str) -> bool:
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or looks_like_toc_entry(stripped):
            continue
        if clean_heading(stripped) == title:
            return True
    return False


def is_heading_line(line: str, supplemental_titles: set[str] | None = None) -> bool:
    supplemental_titles = supplemental_titles or set()
    stripped = line.strip()
    if not stripped or looks_like_toc_entry(stripped):
        return False
    cleaned = clean_heading(stripped)
    return bool(
        MARKDOWN_HEADING_PATTERN.match(stripped)
        or PRIMARY_CHAPTER_PATTERN.match(cleaned)
        or cleaned in supplemental_titles
    )
