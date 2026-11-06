from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Protocol, Dict

@dataclass
class DocSection:
    name: str
    text: str

@dataclass
class ParsedDocument:
    sections: List[DocSection]
    metadata: Optional[Dict] = None

class DocumentParser(Protocol):
    def can_handle(self, filename: str, mime_type: str) -> bool: ...
    def parse(self, content: bytes, filename: str) -> ParsedDocument: ...
