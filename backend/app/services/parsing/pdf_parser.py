import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from app.services.parsing.models import ParsedChapter, ParsedTextbook
from app.services.parsing.chapter_headings import (
    PRIMARY_CHAPTER_PATTERN,
    clean_heading,
    infer_supplemental_titles_from_toc,
    is_heading_line,
    looks_like_toc_entry,
)

PDF_STRING_PATTERN = re.compile(rb"\(([^()]*)\)")

# Lines that look like a chapter subtitle (topic name following "第X章")
TOPIC_LINE = re.compile(r"^[一-鿿]{1,8}$")

# Characters per page above which we consider a page "text-heavy" (not just a chart)
MIN_TEXT_CHARS_FOR_PAGE = 40


def _clean_extracted_text(text: str) -> str:
    """Remove control characters and unmapped glyphs from extracted PDF text."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = text.replace("�", "")
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_heading_text(text: str) -> str:
    """Clean a detected chapter heading: remove noise, trailing numbers, artifacts."""
    text = _clean_extracted_text(text)
    # Remove trailing page numbers that got merged (e.g. "头部9" -> "头部")
    text = re.sub(r"\d{1,4}$", "", text).strip()
    # Remove trailing whitespace-like artifacts
    text = re.sub(r"[\s\t]+$", "", text)
    return text


# ---------------------------------------------------------------------------
# Page-by-page streaming extraction (does not accumulate all pages in memory)
# ---------------------------------------------------------------------------

def _iter_page_texts(path: Path) -> Iterator[tuple[int, str]]:
    """Yield (page_number_zero_based, cleaned_text) for each page.

    Uses fitz.open() which memory-maps the file; pages are extracted and
    yielded one at a time so the full document is never held in memory.
    """
    try:
        import fitz
    except ModuleNotFoundError:
        yield from _iter_simple_pages(path)
        return

    doc = fitz.open(path)
    try:
        for i, page in enumerate(doc):
            text = page.get_text("text")
            text = _clean_extracted_text(text)
            if len(text) >= MIN_TEXT_CHARS_FOR_PAGE:
                yield (i, text)
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Structured (dict) extraction – used for font-aware chapter detection
# ---------------------------------------------------------------------------

def _iter_page_blocks(path: Path) -> Iterator[tuple[int, list[dict[str, Any]]]]:
    """Yield (page_number, text_blocks) for each page.

    Each block is a dict with: text, font_size, is_bold, bbox (y0, y1).
    Image blocks (type=1) are skipped.
    """
    try:
        import fitz
    except ModuleNotFoundError:
        return

    doc = fitz.open(path)
    try:
        for i, page in enumerate(doc):
            blocks: list[dict[str, Any]] = []
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block.get("type") == 1:  # image block – skip
                    continue
                block_text_parts: list[str] = []
                max_size = 0.0
                is_bold = False
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        cleaned = _clean_extracted_text(text)
                        if cleaned:
                            block_text_parts.append(cleaned)
                        size = span.get("size", 0) or 0
                        if size > max_size:
                            max_size = size
                        flags = span.get("flags", 0) or 0
                        if flags & (1 << 3):  # bit 3 = bold in PDF font flags
                            is_bold = True
                if not block_text_parts:
                    continue
                blocks.append({
                    "text": "".join(block_text_parts).strip(),
                    "font_size": max_size,
                    "is_bold": is_bold,
                    "bbox": block.get("bbox", [0, 0, 0, 0]),
                })
            yield (i, blocks)
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Chapter detection combining font analysis + regex
# ---------------------------------------------------------------------------

def _detect_chapter_headings(path: Path, supplemental_titles: set[str]) -> dict[int, str]:
    """Return {page_index: chapter_title} using font size, bold, AND regex.

    Only 第X章 / 绪论 level is considered. Two-line titles like
    "第一章" + "头部" are merged into "第一章 头部".
    """
    headings: dict[int, str] = {}
    for page_idx, blocks in _iter_page_blocks(path):
        if not blocks:
            continue

        sizes = sorted(b["font_size"] for b in blocks if b["font_size"] > 0)
        median_size = sizes[len(sizes) // 2] if sizes else 0

        for i, block in enumerate(blocks):
            candidates = block["text"].splitlines()
            for line in candidates:
                stripped = line.strip()
                cleaned = clean_heading(stripped)
                if looks_like_toc_entry(stripped):
                    continue
                if not (
                    PRIMARY_CHAPTER_PATTERN.match(cleaned)
                    or cleaned in supplemental_titles
                ):
                    continue
                is_larger = block["font_size"] > median_size + 0.5 if median_size > 0 else True
                if not (is_larger or block["is_bold"]):
                    continue

                title = _clean_heading_text(cleaned)
                if not title:
                    continue

                # Check if the next block is a short topic name (e.g. "头部")
                # and merge it into the title
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    next_text = next_block["text"].strip()
                    if TOPIC_LINE.match(next_text) and 1 <= len(next_text) <= 4:
                        # Only merge if the next block is visually similar (size)
                        if abs(next_block["font_size"] - block["font_size"]) < 3:
                            title = f"{title} {next_text}"

                if page_idx not in headings:
                    headings[page_idx] = title

    return headings


# Also try regex-only as fallback (catches headings that font analysis might miss)
def _detect_headings_regex_only(
    page_texts: list[tuple[int, str]],
    supplemental_titles: set[str],
) -> dict[int, str]:
    headings: dict[int, str] = {}
    for page_idx, page_text in page_texts:
        for line in page_text.splitlines():
            stripped = line.strip()
            if is_heading_line(stripped, supplemental_titles):
                title = _clean_heading_text(stripped)
                if title and page_idx not in headings:
                    headings[page_idx] = title
                break
    return headings


# ---------------------------------------------------------------------------
# Header / footer filtering
# ---------------------------------------------------------------------------

def _filter_headers_footers(page_texts: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Remove repeated header/footer lines using edge-line frequency analysis."""
    if len(page_texts) < 3:
        return [(idx, text) for idx, text in page_texts]

    edge_lines: list[str] = []
    per_page_lines: list[tuple[int, list[str]]] = []
    for idx, text in page_texts:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        per_page_lines.append((idx, lines))
        edge_lines.extend(lines[:2])
        edge_lines.extend(lines[-2:])

    repeated = {
        line for line, count in Counter(edge_lines).items()
        if count >= max(2, len(page_texts) // 2)
    }

    result: list[tuple[int, str]] = []
    for idx, lines in per_page_lines:
        filtered = [line for line in lines if line not in repeated]
        result.append((idx, "\n".join(filtered)))
    return result


# ---------------------------------------------------------------------------
# Assemble chapters from page boundaries
# ---------------------------------------------------------------------------

def _assemble_chapters(
    page_texts: list[tuple[int, str]],
    headings: dict[int, str],
    default_title: str,
    total_pages: int,
) -> list[ParsedChapter]:
    """Group pages into chapters using detected heading page indices.

    If the same chapter title appears on multiple pages (e.g. once in TOC
    and once at the real chapter start), keep only the one with more content.
    """
    if not headings:
        combined = "\n\n".join(text.strip() for _, text in page_texts if text.strip())
        return [
            ParsedChapter(
                title=default_title or "PDF Chapter",
                order_index=1,
                content=combined,
                page_start=1,
                page_end=total_pages,
            )
        ]

    sorted_starts = sorted(headings.items())  # [(page_idx, title), ...]
    chapters: list[ParsedChapter] = []

    for order_index, (start_page, title) in enumerate(sorted_starts, start=1):
        next_page = (
            sorted_starts[order_index][0]
            if order_index < len(sorted_starts)
            else total_pages
        )
        content_parts = [
            text for idx, text in page_texts
            if start_page <= idx < next_page and text.strip()
        ]
        content = "\n\n".join(content_parts)
        chapters.append(
            ParsedChapter(
                title=title,
                order_index=order_index,
                content=content,
                page_start=start_page + 1,
                page_end=next_page,
            )
        )

    # Deduplicate: if same title appears multiple times, keep the one with
    # the most content (real chapter > TOC stub)
    seen: dict[str, ParsedChapter] = {}
    for ch in chapters:
        if ch.title in seen:
            if len(ch.content) > len(seen[ch.title].content):
                seen[ch.title] = ch
        else:
            seen[ch.title] = ch

    # Preserve original order using first-appearance order
    order_map = {ch.title: i for i, ch in enumerate(chapters)}
    deduped = sorted(seen.values(), key=lambda ch: order_map[ch.title])

    # Re-number order_index
    for i, ch in enumerate(deduped, start=1):
        ch.order_index = i

    return deduped


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_pdf(path: Path) -> ParsedTextbook:
    """Parse a PDF into a ParsedTextbook.

    Processing is page-by-page: pages are extracted, cleaned, and filtered
    one at a time without loading the entire document into memory.
    Chapter headings are detected using font size, bold flags, AND regex.
    Headers, footers, and image-only areas are filtered out.
    """
    # Step 1: stream pages (never accumulates all pages at once)
    page_texts = list(_iter_page_texts(path))
    total_pages = max(len(page_texts), 1)
    all_lines = [line for _, page_text in page_texts for line in page_text.splitlines()]
    supplemental_titles = infer_supplemental_titles_from_toc(all_lines)

    # Step 2: detect chapter headings (font-aware + regex fallback)
    headings = _detect_chapter_headings(path, supplemental_titles)
    if not headings:
        # Fallback: regex-only detection on extracted text
        headings = _detect_headings_regex_only(page_texts, supplemental_titles)

    # Step 3: filter repeated headers/footers
    filtered_pages = _filter_headers_footers(page_texts)

    # Step 4: assemble chapters
    chapters = _assemble_chapters(filtered_pages, headings, default_title=path.stem, total_pages=total_pages)

    total_chars = sum(len(ch.content) for ch in chapters)
    return ParsedTextbook(
        total_pages=total_pages,
        total_chars=total_chars,
        chapters=chapters,
    )


# ---------------------------------------------------------------------------
# Simple fallback parser (when fitz is unavailable)
# ---------------------------------------------------------------------------

def _safe_decode(data: bytes) -> str:
    for encoding in ("utf-8", "gbk", "gb2312", "latin-1"):
        try:
            return data.decode(encoding).strip()
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="ignore").strip()


def _iter_simple_pages(path: Path) -> Iterator[tuple[int, str]]:
    raw = path.read_bytes()
    page_count = max(raw.count(b"/Type /Page"), raw.count(b"/Page"), 1)
    strings = []
    for match in PDF_STRING_PATTERN.finditer(raw):
        text = match.group(1).replace(rb"\(", b"(").replace(rb"\)", b")")
        decoded = _safe_decode(text)
        if decoded:
            strings.append(decoded)
    text = "\n".join(strings)
    for i in range(page_count):
        yield (i, text if i == 0 else "")


def _parse_simple_pdf_pages(path: Path) -> list[str]:
    return [text for _, text in _iter_simple_pages(path)]
