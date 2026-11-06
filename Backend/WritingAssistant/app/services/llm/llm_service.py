from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
from app.services.llm.llm_client.client import LLMClient

@dataclass
class LLMResult:
    generated_text: str
    status: str = "ok"
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    prompt_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class LLMService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    @property
    def provider(self) -> str:
        return self.llm_client.provider

    @property
    def model(self) -> str:
        return self.llm_client.model

    def generate(self, final_prompt: str) -> LLMResult:
        try:
            text, meta = self.llm_client.generate_text(final_prompt)
            usage = meta.get("usage") or {}
            return LLMResult(
                generated_text=text,
                status="ok",
                prompt_tokens=usage.get("input_tokens"),
                output_tokens=usage.get("output_tokens"),
            )
        except Exception as e:
            return LLMResult(
                generated_text="",
                status="failed",
                error_code="AI_CLIENT_ERROR",
                error_message=str(e),
            )
