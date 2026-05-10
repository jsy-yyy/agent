from app.services.parsing.chapter_headings import infer_supplemental_titles_from_toc
from app.services.parsing.pdf_parser import _detect_headings_regex_only
from app.services.parsing.text_parser import split_text_by_headings


def test_text_parser_uses_toc_titles_like_recommended_reading_as_chapters() -> None:
    text = """
目录
第一章 绪论 ........ 1
第二章 方法 ........ 12
推荐阅读 ........ 200

第一章 绪论
绪论内容

第二章 方法
方法内容

推荐阅读
书目A
书目B
""".strip()

    chapters = split_text_by_headings(text, default_title="sample")

    assert [chapter.title for chapter in chapters] == ["第一章 绪论", "第二章 方法", "推荐阅读"]
    assert chapters[0].content == "绪论内容"
    assert chapters[2].content == "书目A\n书目B"


def test_toc_inference_only_keeps_titles_that_reappear_as_standalone_sections() -> None:
    lines = """
目录
第一章 绪论 ........ 1
第二章 方法 ........ 12
推荐阅读 ........ 200
术语表 ........ 210

第一章 绪论
正文

推荐阅读
书目
""".strip().splitlines()

    assert infer_supplemental_titles_from_toc(lines) == {"推荐阅读"}


def test_pdf_regex_heading_detection_accepts_toc_inferred_titles() -> None:
    page_texts = [
        (0, "目录\n第一章 绪论 ........ 1\n第二章 方法 ........ 12\n推荐阅读 ........ 200"),
        (1, "第一章 绪论\n正文内容"),
        (2, "第二章 方法\n更多内容"),
        (3, "推荐阅读\n参考书目"),
    ]

    headings = _detect_headings_regex_only(page_texts, {"推荐阅读"})

    assert headings == {
        1: "第一章 绪论",
        2: "第二章 方法",
        3: "推荐阅读",
    }
