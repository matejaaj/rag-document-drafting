from pydantic import BaseModel

class CreateModelOutput(BaseModel):
    prompt_execution_id: int
    deleted: int = 0
    generated_text: str
