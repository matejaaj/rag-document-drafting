from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, Text, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class SectionDraft(Base):
    __tablename__ = 'section_draft'
    __table_args__ = (
        ForeignKeyConstraint(['model_output'], ['model_output.id'], name='fk_draft_output'),
        PrimaryKeyConstraint('id', name='sys_c008278')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    model_output: Mapped[Optional[int]] = mapped_column(Integer)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP\n'))

    model_output_: Mapped[Optional['ModelOutput']] = relationship('ModelOutput', back_populates='section_draft')
    section_iteration: Mapped[list['SectionIteration']] = relationship('SectionIteration', back_populates='section_draft')
