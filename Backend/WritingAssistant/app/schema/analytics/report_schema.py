from pydantic import BaseModel
from typing import Optional, List

class SectionSelectionIn(BaseModel):
    section_id: int
    seq_no: Optional[int] = None

class DocumentReportIn(BaseModel):
    title: Optional[str] = None
    selections: List[SectionSelectionIn]
