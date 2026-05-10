from pathlib import Path

from app.services.parsing.markdown_parser import parse_markdown
from app.services.parsing.models import ParsedTextbook
from app.services.parsing.pdf_parser import parse_pdf
from app.services.parsing.text_parser import parse_txt


class ParserService:
    def parse(self, path: Path, file_format: str) -> ParsedTextbook:
        if file_format == "txt":
            return parse_txt(path)
        if file_format == "markdown":
            return parse_markdown(path)
        if file_format == "pdf":
            return parse_pdf(path)
        raise ValueError(f"Unsupported parse format: {file_format}")


parser_service = ParserService()
