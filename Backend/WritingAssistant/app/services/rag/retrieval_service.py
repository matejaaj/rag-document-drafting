from __future__ import annotations
from typing import List, Tuple, Optional, Dict
import re

from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.vector_service import VectorService
from app.model.rag.vector_models import DocumentVector, ChunkVector
from app.services.rag.retrieval_models import (
    RetrievalConfig,
    DocHit,
    ChunkBlock,
    RetrievalResult,
)

class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService, vector_service: VectorService, config: Optional[RetrievalConfig] = None):
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.config = config or RetrievalConfig()

    def retrieve_context(
        self,
        *,
        document_type_id: int,
        global_instruction: str,
        section_instruction: str,
    ) -> RetrievalResult:
        document_query_embedding = self.embedding_service.embed_query(global_instruction)
        document_rows: List[Tuple[DocumentVector, float]] = self.vector_service.search_documents_by_vector(
            query_vector=document_query_embedding,
            limit=self.config.max_documents,
            document_type_id=document_type_id,
        )

        document_hits, top_document_ids, _ = self._select_documents(document_rows)
        if not document_hits:
            return RetrievalResult(doc_hits=[], chunk_blocks=[])

        chunk_query_embedding = self.embedding_service.embed_query(section_instruction)
        candidate_chunk_rows: List[Tuple[ChunkVector, float]] = self.vector_service.search_chunks_by_vector(
            query_vector=chunk_query_embedding,
            limit=self.config.max_chunks * 3,
            document_ids=top_document_ids,
        )

        top_chunk_rows = self._select_top_chunks_with_diversity(
            candidate_chunk_rows, limit=self.config.max_chunks, max_chunks_per_document=self.config.max_chunks_per_document
        )

        chunk_blocks = self._merge_neighbors_into_blocks(top_chunk_rows, candidate_chunk_rows=candidate_chunk_rows)

        return RetrievalResult(
            doc_hits=document_hits,
            chunk_blocks=chunk_blocks,
        )

    def _select_documents(
        self,
        document_rows: List[Tuple[DocumentVector, float]],
    ) -> Tuple[List[DocHit], List[str], List[float]]:
        sorted_document_rows = sorted(document_rows, key=lambda row: float(row[1]))
        selected_rows: List[Tuple[DocumentVector, float]] = []
        for document, distance in sorted_document_rows:
            if len(selected_rows) < self.config.max_documents and distance <= self.config.max_document_distance:
                selected_rows.append((document, distance))
        document_hits: List[DocHit] = [
            DocHit(document_id=document.id, title=document.title, distance=float(distance))
            for document, distance in selected_rows
        ]
        return document_hits, [document.id for document, _ in selected_rows], [float(distance) for _, distance in sorted_document_rows]

    def _select_top_chunks_with_diversity(
        self,
        chunk_rows: List[Tuple[ChunkVector, float]],
        limit: int,
        max_chunks_per_document: int,
    ) -> List[Tuple[ChunkVector, float]]:
        sorted_chunk_rows = sorted(chunk_rows, key=lambda row: float(row[1]))
        chunk_count_per_document: Dict[str, int] = {}
        selected_rows: List[Tuple[ChunkVector, float]] = []
        for chunk, distance in sorted_chunk_rows:
            if chunk_count_per_document.get(chunk.document_id, 0) >= max_chunks_per_document:
                continue
            selected_rows.append((chunk, distance))
            chunk_count_per_document[chunk.document_id] = chunk_count_per_document.get(chunk.document_id, 0) + 1
            if len(selected_rows) >= limit:
                break
        return selected_rows

    def _merge_neighbors_into_blocks(
        self,
        top_chunk_rows: List[Tuple[ChunkVector, float]],
        *,
        candidate_chunk_rows: List[Tuple[ChunkVector, float]],
    ) -> List[ChunkBlock]:
        chunk_rows_by_key: Dict[Tuple[str, int], Tuple[ChunkVector, float]] = {
            (chunk.document_id, chunk.chunk_index): (chunk, distance) for (chunk, distance) in candidate_chunk_rows
        }
        used_keys: set[Tuple[str, int]] = set()
        chunk_blocks: List[ChunkBlock] = []

        for chunk, distance in sorted(top_chunk_rows, key=lambda row: float(row[1])):
            chunk_key = (chunk.document_id, chunk.chunk_index)
            if chunk_key in used_keys:
                continue

            neighbor_keys = [
                (chunk.document_id, chunk.chunk_index - 1),
                chunk_key,
                (chunk.document_id, chunk.chunk_index + 1),
            ]

            chosen_rows: List[Tuple[ChunkVector, float]] = []
            for neighbor_key in neighbor_keys:
                neighbor_row = chunk_rows_by_key.get(neighbor_key)
                if not neighbor_row:
                    continue
                neighbor_chunk, neighbor_distance = neighbor_row
                if (neighbor_chunk.section_name == chunk.section_name) and (
                    neighbor_key == chunk_key or (neighbor_distance <= min(self.config.max_chunk_distance, distance + self.config.neighbor_distance_delta))
                ):
                    chosen_rows.append((neighbor_chunk, neighbor_distance))

            if not chosen_rows:
                continue

            chosen_rows.sort(key=lambda row: row[0].chunk_index)
            merged_text = self._deduplicate_sentences(" ".join(chosen_chunk.text for (chosen_chunk, _) in chosen_rows), section_name=chunk.section_name)
            start_chunk_index = chosen_rows[0][0].chunk_index
            end_chunk_index = chosen_rows[-1][0].chunk_index
            block_distance = min(float(chosen_distance) for (_, chosen_distance) in chosen_rows)

            chunk_blocks.append(ChunkBlock(
                document_id=chunk.document_id,
                section_name=chunk.section_name,
                chunk_indices=(start_chunk_index, end_chunk_index),
                text=merged_text,
                distance=float(block_distance),
            ))
            used_keys.update((chosen_chunk.document_id, chosen_chunk.chunk_index) for (chosen_chunk, _) in chosen_rows)

        return chunk_blocks

    def _deduplicate_sentences(self, text: str, section_name: Optional[str] = None) -> str:
        if not text:
            return ""
        normalized_text = re.sub(r"\s+", " ", text.strip())
        sentences = re.split(r'(?<=[.!?])\s+', normalized_text)
        seen_sentence_keys = set()
        unique_sentences: List[str] = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence_key = sentence.lower()
            if sentence_key in seen_sentence_keys:
                continue
            seen_sentence_keys.add(sentence_key)
            unique_sentences.append(sentence)
        prefix = f"[{section_name}] " if section_name else ""
        return prefix + " ".join(unique_sentences)
