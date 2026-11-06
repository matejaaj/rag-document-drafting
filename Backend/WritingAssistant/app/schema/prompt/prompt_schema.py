from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schema.prompt.prompt_version_schema import PromptVersionOut
from app.schema.common.pagination_schema import PaginationMeta

class CreatePrompt(BaseModel):
    title: str
    document_type_id: int
    created_by: Optional[int] = None
    deleted: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PromptOut(BaseModel):
    id: int
    title: str
    document_type_id: int
    is_active: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


class PromptQuery(BaseModel):
    page: int = 1
    per_page: int = 20
    ordering: str = "-updated_at"
    title: Optional[str] = None
    document_type_id: Optional[int] = None
    deleted: int = 0


class PromptWithActiveVersionOut(BaseModel):
    id: int
    title: str
    document_type_id: int
    is_active: bool
    active_version: Optional[PromptVersionOut] = None
    updated_at: Optional[datetime] = None


class PromptWithActiveVersionPageOut(BaseModel):
    items: list[PromptWithActiveVersionOut]
    meta: PaginationMeta


class PatchPromptTitle(BaseModel):
    title: str
    updated_at: Optional[datetime] = None
