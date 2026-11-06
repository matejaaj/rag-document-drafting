from __future__ import annotations
from typing import List
import re


class ChunkingService:
    def __init__(
        self,
        max_model_tokens: int = 512,
        target_tokens: int = 360,
        overlap_tokens: int = 64,
        passage_prefix: str = "passage: ",
        reserve_tokens: int = 8,
        avg_chars_per_token: int = 4,
    ):
        self.max_model_tokens = max_model_tokens
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.passage_prefix = passage_prefix
        self.reserve_tokens = reserve_tokens
        self.avg_chars_per_token = avg_chars_per_token

    def _clean_whitespace(self, text: str) -> str:
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
        return text.strip()

    def make_chunks(self, text: str) -> List[str]:
        text = self._clean_whitespace(text)
        if not text:
            return []

        prefix_tokens = len(self.passage_prefix) // self.avg_chars_per_token
        hard_cap_tokens = max(16, self.max_model_tokens - prefix_tokens - self.reserve_tokens)
        hard_cap_chars = hard_cap_tokens * self.avg_chars_per_token

        if len(text) <= hard_cap_chars:
            return [text]

        window_tokens = min(self.target_tokens, hard_cap_tokens)
        stride_tokens = max(1, window_tokens - self.overlap_tokens)
        window_chars = window_tokens * self.avg_chars_per_token
        stride_chars = stride_tokens * self.avg_chars_per_token

        chunks: List[str] = []
        window_start = 0
        text_length = len(text)
        while window_start < text_length:
            window_end = min(window_start + window_chars, text_length)
            piece = text[window_start:window_end]
            if len(piece) > hard_cap_chars:
                piece = piece[:hard_cap_chars]
            if piece.strip():
                chunks.append(piece.strip())
            if window_end >= text_length:
                break
            window_start += stride_chars

        return chunks
