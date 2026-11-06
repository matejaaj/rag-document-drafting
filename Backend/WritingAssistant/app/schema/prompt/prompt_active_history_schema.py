from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreatePromptActiveHistory(BaseModel):
    prompt_version_id: int
    document_type_id: int
    activated_by: Optional[int] = None
    activated_at: Optional[datetime] = None
    deleted: int = 0
