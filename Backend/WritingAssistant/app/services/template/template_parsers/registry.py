from typing import List
from .protocol import TemplateParser
from .markdown import MarkdownTemplateParser

_TEMPLATE_PARSERS: List[TemplateParser] = [
    MarkdownTemplateParser(),

]

def pick_template_parser(filename: str, mime_type: str) -> TemplateParser:
    for parser in _TEMPLATE_PARSERS:
        if parser.can_handle(filename, mime_type):
            return parser
    raise ValueError(f"Nepodržan tip fajla: {filename} ({mime_type})")
