from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schema.common.pagination_schema import PaginationMeta

class CreateDocumentType(BaseModel):
    name: str
    description: Optional[str] = None
    deleted: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DocumentTypeOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    deleted: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentTypeQuery(BaseModel):
    page: int = 1
    per_page: int = 20
    ordering: str = "-updated_at"
    name: Optional[str] = None
    deleted: int = 0

class DocumentTypePageOut(BaseModel):
    items: List[DocumentTypeOut]
    meta: PaginationMeta


class UpdateDocumentType(BaseModel):
    name: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
