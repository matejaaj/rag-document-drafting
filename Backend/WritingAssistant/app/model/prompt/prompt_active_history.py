from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class PromptActiveHistory(Base):
    __tablename__ = 'prompt_active_history'
    __table_args__ = (
        ForeignKeyConstraint(['prompt_version_id'], ['prompt_version.id'], name='fk_prompt_history'),
        ForeignKeyConstraint(['document_type_id'], ['document_type.id'], name='fk_pah_doc_type'),
        PrimaryKeyConstraint('id', name='sys_c008246')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_version_id: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    activated_by: Mapped[Optional[int]] = mapped_column(Integer)
    activated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP\n'))

    prompt_version: Mapped['PromptVersion'] = relationship('PromptVersion', back_populates='prompt_active_history')
