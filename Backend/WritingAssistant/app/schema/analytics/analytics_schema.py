from pydantic import BaseModel
from typing import Optional

class AnalyticsOut(BaseModel):
    scope: str
    prompt_id: Optional[int] = None
    prompt_version_id: Optional[int] = None

    num_executions: int
    avg_duration_ms: Optional[float]
    avg_input_tokens: Optional[float]
    avg_output_tokens: Optional[float]
    avg_tokens: Optional[float]
    total_tokens: int
    cost_per_execution: Optional[float]
    total_cost_usd: float
    error_rate: Optional[float]

    rating_count: int
    rating_avg: Optional[float]
    rating_median: Optional[float]
    rating_c1: int
    rating_c2: int
    rating_c3: int
    rating_c4: int
    rating_c5: int

    failed_execution_count: Optional[int] = None
    bayes_score: Optional[float] = None
