from __future__ import annotations
from typing import Optional
import weaviate
from app.core.config import SETTINGS

_weaviate_client: Optional[weaviate.WeaviateClient] = None

def get_client() -> weaviate.WeaviateClient:
    global _weaviate_client
    if _weaviate_client is None:
        _weaviate_client = weaviate.connect_to_custom(
            http_host=SETTINGS.weaviate.http_host,
            http_port=SETTINGS.weaviate.http_port,
            http_secure=SETTINGS.weaviate.http_secure,
            grpc_host=SETTINGS.weaviate.grpc_host,
            grpc_port=SETTINGS.weaviate.grpc_port,
            grpc_secure=SETTINGS.weaviate.grpc_secure,
        )
    return _weaviate_client

def is_ready() -> bool:
    return get_client().is_ready()

def close() -> None:
    global _weaviate_client
    if _weaviate_client:
        _weaviate_client.close()
        _weaviate_client = None
