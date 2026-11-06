from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CreateSectionInstruction(BaseModel):
    session_section_id: int
    text_: str
    deleted: Optional[int] = 0
    created_at: Optional[datetime] = None


class SectionInstructionOut(BaseModel):
    id: int
    session_section_id: int
    text_: str
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
