from __future__ import annotations
from typing import Optional

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Text, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class ModelOutput(Base):
    __tablename__ = 'model_output'
    __table_args__ = (
        ForeignKeyConstraint(['prompt_execution_id'], ['prompt_execution.id'], name='fk_output_exec'),
        PrimaryKeyConstraint('id', name='sys_c008275')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_execution_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    generated_text: Mapped[Optional[str]] = mapped_column(Text)

    prompt_execution: Mapped['PromptExecution'] = relationship('PromptExecution', back_populates='model_output')
    output_feedback: Mapped[list['OutputFeedback']] = relationship('OutputFeedback', back_populates='model_output')
    section_draft: Mapped[list['SectionDraft']] = relationship('SectionDraft', back_populates='model_output_')
    section_iteration: Mapped[list['SectionIteration']] = relationship('SectionIteration', back_populates='model_output')
