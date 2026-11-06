from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

DOCUMENT_COLL = "Document"
CHUNK_COLL = "Chunk"

class DocumentVector(BaseModel):
    id: str
    storage_object_id: int
    document_type_id: int
    title: Optional[str] = None
    summary_text: Optional[str] = None
    created_at: Optional[datetime] = None


class ChunkVector(BaseModel):
    id: str
    document_id: str
    storage_object_id: int
    document_type_id: int
    section_name: str
    chunk_index: int
    text: str
    created_at: Optional[datetime] = None
