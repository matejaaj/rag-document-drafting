from __future__ import annotations
from typing import List, Any
import numpy as np
from huggingface_hub import InferenceClient
from app.core.config import SETTINGS

class EmbeddingService:
    provider: str
    model: str

    def __init__(self):
        if not SETTINGS.hf.api_key:
            raise RuntimeError("HF_TOKEN nije setovan u okruženju.")
        self._inference_client = InferenceClient(token=SETTINGS.hf.api_key)
        self.provider = "huggingface"
        self.model = SETTINGS.hf.model

    def _to_float_list(self, raw_embedding: Any) -> List[float]:
        embedding_array = raw_embedding if isinstance(raw_embedding, np.ndarray) else np.array(raw_embedding, dtype=np.float32)
        if embedding_array.ndim == 2 and embedding_array.shape[0] == 1:
            embedding_array = embedding_array[0]
        return embedding_array.astype(np.float32).tolist()

    def embed_query(self, text: str) -> List[float]:
        raw_embedding = self._inference_client.feature_extraction(f"query: {text}", model=self.model)
        return self._to_float_list(raw_embedding)

    def embed_passage(self, text: str) -> List[float]:
        raw_embedding = self._inference_client.feature_extraction(f"passage: {text}", model=self.model)
        return self._to_float_list(raw_embedding)
