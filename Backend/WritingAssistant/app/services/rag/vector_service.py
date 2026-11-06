from __future__ import annotations
from typing import List, Tuple

from app.model.rag.vector_models import DocumentVector, ChunkVector
from app.repository.rag.vector_repository import VectorRepository
from app.core.exceptions import NotFoundError


class VectorService:
    def __init__(self, vector_repository: VectorRepository):
        self.vector_repository = vector_repository

    def upsert_document_summary(self, document: DocumentVector, vector: List[float]) -> str:
        return self.vector_repository.insert_document(document, vector)

    def upsert_chunks(self, chunks_with_vectors: List[Tuple[ChunkVector, List[float]]]) -> None:
        self.vector_repository.batch_insert_chunks(chunks_with_vectors)

    def search_documents_by_vector(
        self, *, query_vector: List[float], limit: int, document_type_id: int
    ) -> List[Tuple[DocumentVector, float]]:
        rows = self.vector_repository.query_documents_by_vector(
            query_vector=query_vector, limit=limit, document_type_id=document_type_id
        )
        return [
            (
                DocumentVector(
                    id=row["uuid"],
                    storage_object_id=row["properties"].get("storage_object_id"),
                    document_type_id=row["properties"].get("document_type_id"),
                    title=row["properties"].get("title"),
                    summary_text=row["properties"].get("summary_text"),
                    created_at=row["properties"].get("created_at"),
                ),
                row["distance"] if row["distance"] is not None else float("inf"),
            )
            for row in rows
        ]

    def search_chunks_by_vector(
        self, *, query_vector: List[float], limit: int, document_ids: List[str]
    ) -> List[Tuple[ChunkVector, float]]:
        rows = self.vector_repository.query_chunks_by_vector(
            query_vector=query_vector, limit=limit, document_ids=document_ids
        )
        return [
            (
                ChunkVector(
                    id=row["uuid"],
                    document_id=row["properties"].get("document_id"),
                    storage_object_id=row["properties"].get("storage_object_id"),
                    document_type_id=row["properties"].get("document_type_id"),
                    section_name=row["properties"].get("section_name"),
                    chunk_index=row["properties"].get("chunk_index"),
                    text=row["properties"].get("text"),
                    created_at=row["properties"].get("created_at"),
                ),
                row["distance"] if row["distance"] is not None else 1.0,
            )
            for row in rows
        ]

    def get_summary(self, storage_object_id: int) -> str:
        summary_text = self.vector_repository.get_summary_text_by_storage_object_id(storage_object_id)
        if not summary_text:
            raise NotFoundError(detail="Dokument nema sažetak")
        return summary_text

    def delete_by_storage_object_id(self, storage_object_id: int) -> None:
        self.vector_repository.delete_by_storage_object_id(storage_object_id)
