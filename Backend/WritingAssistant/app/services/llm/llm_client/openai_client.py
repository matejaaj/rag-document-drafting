from __future__ import annotations
from typing import Any, Dict, Tuple, List
from openai import OpenAI
from app.core.config import SETTINGS

class OpenAIClient:
    provider: str
    model: str

    def __init__(self):
        if not SETTINGS.openai.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self._client = OpenAI(
            api_key=SETTINGS.openai.api_key,
            base_url=SETTINGS.openai.base_url,
        )
        self.provider = "openai"
        self.model = SETTINGS.openai.model

    def _extract_text(self, response: Any) -> str:
        text_parts: List[str] = []
        output_items = getattr(response, "output", None) or []
        for output_item in output_items:
            content_parts = getattr(output_item, "content", None) or []
            for content_part in content_parts:
                if getattr(content_part, "type", None) == "output_text":
                    text = getattr(content_part, "text", "") or ""
                    if text:
                        text_parts.append(text)
        if not text_parts:
            output_text = getattr(response, "output_text", None)
            if output_text:
                text_parts.append(str(output_text))
        return "\n".join(text_parts).strip()

    def _usage_to_dict(self, usage_object: Any) -> Dict[str, Any]:
        if not usage_object:
            return {}
        if isinstance(usage_object, dict):
            return {
                "input_tokens": usage_object.get("input_tokens"),
                "output_tokens": usage_object.get("output_tokens"),
                "total_tokens": usage_object.get("total_tokens"),
                "input_tokens_details": usage_object.get("input_tokens_details"),
                "output_tokens_details": usage_object.get("output_tokens_details"),
            }
        return {
            "input_tokens": getattr(usage_object, "input_tokens", None),
            "output_tokens": getattr(usage_object, "output_tokens", None),
            "total_tokens": getattr(usage_object, "total_tokens", None),
            "input_tokens_details": getattr(usage_object, "input_tokens_details", None),
            "output_tokens_details": getattr(usage_object, "output_tokens_details", None),
        }

    def generate_text(self, final_prompt: str) -> Tuple[str, Dict[str, Any]]:
        response = self._client.responses.create(
            model=self.model,
            input=final_prompt,
        )
        generated_text = self._extract_text(response)
        usage = self._usage_to_dict(getattr(response, "usage", None))
        meta: Dict[str, Any] = {
            "usage": usage,
            "raw_response": response,
            "model": getattr(response, "model", None),
            "status": getattr(response, "status", None),
            "id": getattr(response, "id", None),
        }
        return generated_text, meta
