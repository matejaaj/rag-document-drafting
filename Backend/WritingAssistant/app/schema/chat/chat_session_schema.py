from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.schema.common.pagination_schema import PaginationMeta

class CreateTestChatSession(BaseModel):
    title: Optional[str] = None
    document_type_id: Optional[int] = None
    template_id: Optional[int] = None
    test_prompt_version_id: Optional[int] = None

    created_by: Optional[int] = None
    deleted: int = 0
    is_test_session: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CreateChatSession(BaseModel):
    template_id: int
    created_by: Optional[int] = None
    document_type_id: Optional[int] = None
    deleted: Optional[int] = 0
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatSessionOut(BaseModel):
    id: int
    template_id: int
    created_by: int
    title: Optional[str]
    updated_at: Optional[datetime]
    document_type_id: int

    is_test_session: Optional[int] = 0
    test_prompt_version_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ChatSessionQuery(BaseModel):
    created_by: int
    deleted: int = 0
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1)
    ordering: str = "-updated_at"


class ChatSessionPageOut(BaseModel):
    items: List[ChatSessionOut]
    meta: PaginationMeta


class PatchChatSessionTitle(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    updated_at: Optional[datetime] = None


class PatchChatSessionDocumentType(BaseModel):
    document_type_id: int
    updated_at: datetime
