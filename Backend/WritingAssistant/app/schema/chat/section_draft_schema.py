from typing import Optional
from pydantic import BaseModel, ConfigDict

class CreateSectionDraft(BaseModel):
    created_by: Optional[int]
    content: Optional[str] = None
    model_output: Optional[int] = None
    deleted: int = 0

class SectionDraftOut(BaseModel):
    id: int
    content: Optional[str] = None


    model_config = ConfigDict(from_attributes=True)

class SaveDraftIn(BaseModel):
    content: str
