from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ModelOutputOut(BaseModel):
    id: int
    generated_text: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SectionInstructionOut(BaseModel):
    id: int
    text_: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class GenerateIterationIn(BaseModel):
    section_instruction: Optional[str] = None
    global_instruction: Optional[str] = None


class CreateSectionIteration(BaseModel):
    seq_no: int
    session_id: int
    session_section_id: int
    deleted: int = 0
    section_instruction_id: Optional[int] = None
    model_output_id: Optional[int] = None
    section_draft_id: Optional[int] = None

class SectionDraftOut(BaseModel):
    id: int
    created_by: Optional[int] = None
    content: Optional[str] = None
    model_output: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SectionIterationOut(BaseModel):
    id: int
    seq_no: int
    session_section_id: int
    section_instruction: Optional[SectionInstructionOut] = None
    model_output: Optional[ModelOutputOut] = None
    section_draft: Optional[SectionDraftOut] = None


    model_config = ConfigDict(from_attributes=True)
