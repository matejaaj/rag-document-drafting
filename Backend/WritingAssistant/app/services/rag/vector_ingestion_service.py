from __future__ import annotations
from typing import List, Tuple, Optional
from uuid import uuid4
from datetime import datetime, timezone

from app.services.rag.document_parser.registry import pick_document_parser
from app.services.rag.summarization_service import SummarizationService
from app.services.rag.chunking_service import ChunkingService
from app.services.rag.embedding_service import EmbeddingService

from app.model.rag.vector_models import DocumentVector, ChunkVector
from app.services.rag.vector_service import VectorService


class VectorIngestionService:
    def __init__(
        self,
        vector_service: VectorService,
        summarization_service: SummarizationService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
    ):
        self.vector_service = vector_service
        self.summarization_service = summarization_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    def ingest_uploaded_document(
        self,
        *,
        content: bytes,
        filename: str,
        mime_type: Optional[str],
        storage_object_id: int,
        document_type_id: int,
        title: Optional[str] = None,
    ) -> str:
        parser = pick_document_parser(filename, mime_type or "")
        parsed_document = parser.parse(content, filename)
        sections = parsed_document.sections

        full_text = "\n\n".join(
            f"# {section.name}\n{section.text}" for section in sections if section.text and section.text.strip()
        )
        summary_text = self.summarization_service.summarize(full_text)

        document_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        summary_embedding = self.embedding_service.embed_passage(summary_text)

        document = DocumentVector(
            id=document_id,
            storage_object_id=storage_object_id,
            document_type_id=document_type_id,
            title=title or filename,
            summary_text=summary_text,
            created_at=created_at,
        )
        self.vector_service.upsert_document_summary(document, summary_embedding)

        chunks_with_embeddings: List[Tuple[ChunkVector, List[float]]] = []
        chunk_index = 0
        for section in sections:
            if not (section.text and section.text.strip()):
                continue
            for chunk_text in self.chunking_service.make_chunks(section.text):
                chunk = ChunkVector(
                    id=str(uuid4()),
                    document_id=document_id,
                    storage_object_id=storage_object_id,
                    document_type_id=document_type_id,
                    section_name=section.name,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    created_at=created_at,
                )
                chunk_embedding = self.embedding_service.embed_passage(chunk_text)
                chunks_with_embeddings.append((chunk, chunk_embedding))

                chunk_index += 1

        if chunks_with_embeddings:
            self.vector_service.upsert_chunks(chunks_with_embeddings)


        return document_id
