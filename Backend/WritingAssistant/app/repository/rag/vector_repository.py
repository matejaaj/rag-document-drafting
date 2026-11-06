from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timezone

from weaviate.classes.query import Filter, MetadataQuery
from app.core.vector_client import get_client
from app.model.rag.vector_models import DOCUMENT_COLL, CHUNK_COLL, DocumentVector, ChunkVector


def _to_properties(model) -> Dict[str, Any]:
    properties = model.model_dump(exclude_none=True)
    properties.pop("id", None)
    created_at = properties.get("created_at")
    if isinstance(created_at, datetime):
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        properties["created_at"] = created_at.isoformat()
    return properties


def _to_rows(response) -> List[Dict[str, Any]]:
    return [
        {
            "uuid": str(result_object.uuid),
            "distance": result_object.metadata.distance,
            "properties": result_object.properties or {},
        }
        for result_object in response.objects
    ]


class VectorRepository:
    def __init__(self) -> None:
        self._weaviate_client = get_client()

    def _document_collection(self):
        return self._weaviate_client.collections.get(DOCUMENT_COLL)

    def _chunk_collection(self):
        return self._weaviate_client.collections.get(CHUNK_COLL)

    def insert_document(self, document: DocumentVector, vector: List[float]) -> str:
        inserted_uuid = self._document_collection().data.insert(properties=_to_properties(document), vector=vector, uuid=document.id)
        return str(inserted_uuid)

    def batch_insert_chunks(self, chunks_with_vectors: Iterable[Tuple[ChunkVector, List[float]]]) -> None:
        chunk_collection = self._chunk_collection()
        with chunk_collection.batch.dynamic() as batch:
            for chunk, vector in chunks_with_vectors:
                batch.add_object(properties=_to_properties(chunk), vector=vector, uuid=chunk.id)

    def query_documents_by_vector(
        self, *, query_vector: List[float], limit: int, document_type_id: int
    ) -> List[Dict[str, Any]]:
        response = self._document_collection().query.near_vector(
            near_vector=query_vector,
            limit=limit,
            filters=Filter.by_property("document_type_id").equal(document_type_id),
            return_metadata=MetadataQuery(distance=True),
        )
        return _to_rows(response)

    def query_chunks_by_vector(
        self, *, query_vector: List[float], limit: int, document_ids: List[str]
    ) -> List[Dict[str, Any]]:
        response = self._chunk_collection().query.near_vector(
            near_vector=query_vector,
            limit=limit,
            filters=Filter.any_of([Filter.by_property("document_id").equal(document_id) for document_id in document_ids]),
            return_metadata=MetadataQuery(distance=True),
        )
        return _to_rows(response)

    def get_summary_text_by_storage_object_id(self, storage_object_id: int) -> Optional[str]:
        storage_object_filter = Filter.by_property("storage_object_id").equal(storage_object_id)
        response = self._document_collection().query.fetch_objects(filters=storage_object_filter, limit=1)
        if not response.objects:
            return None
        return (response.objects[0].properties or {}).get("summary_text")

    def delete_by_storage_object_id(self, storage_object_id: int) -> None:
        storage_object_filter = Filter.by_property("storage_object_id").equal(storage_object_id)
        self._document_collection().data.delete_many(where=storage_object_filter)
        self._chunk_collection().data.delete_many(where=storage_object_filter)
