from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schema.common.pagination_schema import PaginationMeta

class StorageObjectOut(BaseModel):
    id: int
    original_name: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    repo_folder_id: Optional[int] = None
    path: str
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

class StorageObjectPageOut(BaseModel):
    items: List[StorageObjectOut]
    meta: PaginationMeta

class StorageObjectQuery(BaseModel):
    page: int = 1
    per_page: int = 20
    ordering: str = "-created_at"
    deleted: int = 0
    repo_folder_id: Optional[int] = None
    original_name: Optional[str] = None
    mime_type: Optional[str] = None
    created_by: Optional[int] = None

class PatchStorageObject(BaseModel):
    original_name: Optional[str] = None
    repo_folder_id: Optional[int] = None
