from __future__ import annotations
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from typing import Callable, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.repository.base_repository import BaseRepository
from app.model.llm.model_pricing import ModelPricing


class ModelPricingRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, ModelPricing)

    def find_active(
        self,
        provider: str,
        model: str,
        when: Optional[datetime] = None,
    ) -> Optional[ModelPricing]:
        when = when or datetime.now(timezone.utc)
        with self.session_factory() as session:
            query = (
                session.query(ModelPricing)
                .filter(
                    ModelPricing.deleted == 0,
                    ModelPricing.provider == provider,
                    ModelPricing.model == model,
                    ModelPricing.effective_from <= when,
                    or_(
                        ModelPricing.effective_to.is_(None),
                        ModelPricing.effective_to > when,
                    ),
                )
                .order_by(ModelPricing.effective_from.desc())
                .limit(1)
            )
            return query.first()
