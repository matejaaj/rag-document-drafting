from __future__ import annotations
from typing import Optional
import datetime
import decimal

from sqlalchemy import PrimaryKeyConstraint, TIMESTAMP, VARCHAR, text, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class ModelPricing(Base):
    __tablename__ = 'model_pricing'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sys_c008272'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    provider: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    model: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    prompt_token_usd: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(19, 8))
    completion_token_usd: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(19, 8))
    effective_from: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(timezone=False))
    effective_to:   Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(timezone=False))

    prompt_execution: Mapped[list['PromptExecution']] = relationship('PromptExecution', back_populates='pricing')
