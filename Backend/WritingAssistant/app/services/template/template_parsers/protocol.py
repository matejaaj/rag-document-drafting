from __future__ import annotations
from typing import Protocol, Optional, List, Dict
from dataclasses import dataclass

@dataclass
class ParsedTemplate:
    sections: List[str]
    json_schema: Optional[Dict] = None

class TemplateParser(Protocol):
    def can_handle(self, filename: str, mime_type: str) -> bool: ...
    def parse(self, content: bytes, filename: str) -> ParsedTemplate: ...
