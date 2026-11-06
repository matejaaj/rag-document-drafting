from pydantic import BaseModel

class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total_count: int
