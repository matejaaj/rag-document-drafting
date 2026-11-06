from __future__ import annotations
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from app.repository.llm.model_pricing_repository import ModelPricingRepository
from app.services.llm.llm_service import LLMResult, LLMService


class ModelPricingService:
    def __init__(self, model_pricing_repository: ModelPricingRepository, llm_service: LLMService):
        self.model_pricing_repository = model_pricing_repository
        self.llm_service = llm_service

    def calculate_cost(self, llm_result: LLMResult, when: datetime) -> tuple[Optional[int], Optional[Decimal]]:
        pricing = self.model_pricing_repository.find_active(
            provider=self.llm_service.provider,
            model=self.llm_service.model,
            when=when,
        )
        if not pricing:
            return None, None
        if llm_result.status != "ok":
            return pricing.id, None
        cost_usd = (
            Decimal(llm_result.prompt_tokens or 0) * (pricing.prompt_token_usd or Decimal("0"))
            + Decimal(llm_result.output_tokens or 0) * (pricing.completion_token_usd or Decimal("0"))
        ) / Decimal(1_000_000)
        return pricing.id, cost_usd.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
