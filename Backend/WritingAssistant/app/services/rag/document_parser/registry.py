from __future__ import annotations
from typing import List, Optional
from .protocol import DocumentParser
from .pdf import PdfDocumentParser

_PARSERS: List[DocumentParser] = [
    PdfDocumentParser(),
]

def pick_document_parser(filename: str, mime_type: Optional[str] = None) -> DocumentParser:
    normalized_mime_type = (mime_type or "").lower()
    for parser in _PARSERS:
        if parser.can_handle(filename, normalized_mime_type):
            return parser
    raise ValueError(f"Nepodržan tip fajla: {filename} ({mime_type})")
