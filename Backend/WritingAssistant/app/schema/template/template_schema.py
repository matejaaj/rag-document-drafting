from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schema.common.pagination_schema import PaginationMeta


class TemplateOut(BaseModel):
    id: int
    name: str
    document_type_id: int
    updated_at: Optional[datetime] = None
    document_type_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TemplateQuery(BaseModel):
    page: int = 1
    per_page: int = 20
    ordering: str = "-updated_at"
    deleted: int = 0


class TemplatePageOut(BaseModel):
    items: List[TemplateOut]
    meta: PaginationMeta


class TemplateSectionOut(BaseModel):
    id: int
    name: str
    position: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TemplateWithSectionsOut(BaseModel):
    id: int
    name: str
    document_type_id: int
    sections: List[TemplateSectionOut] = []
