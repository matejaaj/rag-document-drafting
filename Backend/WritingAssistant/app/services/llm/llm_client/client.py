from __future__ import annotations
from typing import Protocol, Tuple, Dict, Any

class LLMClient(Protocol):
    provider: str
    model: str

    def generate_text(self, final_prompt: str) -> Tuple[str, Dict[str, Any]]:
        ...
