from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schema.common.pagination_schema import PaginationMeta


class RepoFolderOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RepoFolderQuery(BaseModel):
    page: int = 1
    per_page: int = 20
    ordering: str = "-created_at"
    deleted: int = 0
    parent_id: Optional[int] = None
    name: Optional[str] = None
    created_by: Optional[int] = None


class CreateRepoFolder(BaseModel):
    name: str
    parent_id: Optional[int] = None
    created_by: Optional[int] = None
    deleted: int = 0


class PatchRepoFolder(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class RepoFolderPageOut(BaseModel):
    items: List[RepoFolderOut]
    meta: PaginationMeta
