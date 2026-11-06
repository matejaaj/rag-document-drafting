from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, VARCHAR, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class Prompt(Base):
    __tablename__ = 'prompt'
    __table_args__ = (
        ForeignKeyConstraint(['document_type_id'], ['document_type.id'], name='fk_prompt_doc_type'),
        PrimaryKeyConstraint('id', name='sys_c008238')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    document_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True))

    document_type: Mapped['DocumentType'] = relationship('DocumentType', back_populates='prompt')
    prompt_version: Mapped[list['PromptVersion']] = relationship('PromptVersion', back_populates='prompt')
