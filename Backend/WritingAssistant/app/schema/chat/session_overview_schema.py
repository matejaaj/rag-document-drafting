from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schema.chat.section_iteration_schema import SectionIterationOut


class SessionSectionWithLatestOut(BaseModel):
    id: int
    session_id: int
    name: Optional[str] = None
    position: Optional[int] = None
    latest_iteration: Optional[SectionIterationOut] = None
    model_config = ConfigDict(from_attributes=True)


class SessionOverviewOut(BaseModel):
    document_type_id: int
    latest_global_instruction_text: str
    title: str
    sections: List[SessionSectionWithLatestOut]
