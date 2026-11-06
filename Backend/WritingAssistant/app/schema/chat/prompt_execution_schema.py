from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CreatePromptExecution(BaseModel):
    prompt_version_id: int
    session_id: int
    status: str
    created_by: int
    deleted: int = 0
    section_instruction_id: Optional[int] = None
    global_instruction_id: Optional[int] = None
    final_prompt: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    prompt_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    pricing_id: Optional[int] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
