from pydantic import BaseModel, ConfigDict
from typing import Optional


class CreateSessionSection(BaseModel):
    session_id: int
    template_section_id: Optional[int] = None
    name: str
    position: int
    deleted: Optional[int] = 0


class SessionSectionOut(BaseModel):
    id: int
    session_id: int
    template_section_id: Optional[int]
    name: str
    position: int

    model_config = ConfigDict(from_attributes=True)


class PatchSessionSectionTitle(BaseModel):
    name: str
