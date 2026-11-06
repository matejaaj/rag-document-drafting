import re
from .protocol import ParsedTemplate

class MarkdownTemplateParser:
    """Each # and ## heading becomes a section."""

    _HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,2})\s+(.+?)\s*$", re.MULTILINE)

    def can_handle(self, filename: str, mime_type: str) -> bool:
        extension = filename.rsplit(".", 1)[-1].lower()
        return extension == "md" or mime_type in {"text/markdown"}

    def parse(self, content: bytes, filename: str) -> ParsedTemplate:
        text = content.decode("utf-8", errors="replace")
        section_titles = [match.group(2).strip() for match in self._HEADING_PATTERN.finditer(text)]
        if not section_titles:
            section_titles = [filename.rsplit(".", 1)[0] or "Sekcija"]
        return ParsedTemplate(sections=section_titles)
