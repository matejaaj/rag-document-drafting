from __future__ import annotations
from typing import Optional
import os
from dataclasses import dataclass

def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y"}

@dataclass(frozen=True)
class OpenAISettings:
    api_key: str
    base_url: str
    model: str

@dataclass(frozen=True)
class WeaviateSettings:
    http_host: str
    http_port: int
    grpc_host: str
    grpc_port: int
    http_secure: bool
    grpc_secure: bool
    api_key: Optional[str] = None

@dataclass(frozen=True)
class HFSettings:
    api_key: str
    model: str
    provider: str = "hf-inference"

@dataclass(frozen=True)
class AppSettings:
    openai: OpenAISettings
    weaviate: WeaviateSettings
    hf: HFSettings

def load_settings() -> AppSettings:
    return AppSettings(
        openai=OpenAISettings(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06"),
        ),
        weaviate=WeaviateSettings(
            http_host=os.getenv("WEAVIATE_HTTP_HOST", "weaviate"),
            http_port=int(os.getenv("WEAVIATE_HTTP_PORT", "8080")),
            grpc_host=os.getenv("WEAVIATE_GRPC_HOST", "weaviate"),
            grpc_port=int(os.getenv("WEAVIATE_GRPC_PORT", "50051")),
            http_secure=_as_bool(os.getenv("WEAVIATE_HTTP_SECURE", "false")),
            grpc_secure=_as_bool(os.getenv("WEAVIATE_GRPC_SECURE", "false")),
            api_key=os.getenv("WEAVIATE_API_KEY"),
        ),
        hf=HFSettings(
            api_key=os.getenv("HF_TOKEN", ""),
            model=os.getenv("HF_MODEL", "intfloat/multilingual-e5-large"),
            provider=os.getenv("HF_PROVIDER", "hf-inference"),
        ),
    )

SETTINGS = load_settings()
