from __future__ import annotations
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RetrievalConfig:
    max_documents: int = 4
    max_document_distance: float = 0.5
    max_chunks: int = 3
    max_chunks_per_document: int = 2
    max_chunk_distance: float = 0.5
    neighbor_distance_delta: float = 0.10


@dataclass
class DocHit:
    document_id: str
    title: Optional[str]
    distance: float


@dataclass
class ChunkBlock:
    document_id: str
    section_name: Optional[str]
    chunk_indices: Tuple[int, int]
    text: str
    distance: float


@dataclass
class RetrievalResult:
    doc_hits: List[DocHit]
    chunk_blocks: List[ChunkBlock]
