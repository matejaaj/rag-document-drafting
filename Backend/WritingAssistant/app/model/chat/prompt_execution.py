from __future__ import annotations
from typing import Optional
import datetime
import decimal

from sqlalchemy import Enum, ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, Text, VARCHAR, text, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class PromptExecution(Base):
    __tablename__ = 'prompt_execution'
    __table_args__ = (

        ForeignKeyConstraint(['global_instruction_id'], ['global_instruction.id'], name='fk_exec_global_instr'),
        ForeignKeyConstraint(['pricing_id'], ['model_pricing.id'], name='fk_exec_pricing'),
        ForeignKeyConstraint(['prompt_version_id'], ['prompt_version.id'], name='fk_exec_prompt_ver'),
        ForeignKeyConstraint(['section_instruction_id'], ['section_instruction.id'], name='fk_exec_section_instr'),
        ForeignKeyConstraint(['session_id'], ['chat_session.id'], name='fk_exec_session'),
        PrimaryKeyConstraint('id', name='sys_c008270')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_version_id: Mapped[int] = mapped_column(Integer, nullable=False)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Enum('ok', 'failed'), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    section_instruction_id: Mapped[Optional[int]] = mapped_column(Integer)
    global_instruction_id: Mapped[Optional[int]] = mapped_column(Integer)
    final_prompt: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(19, 8))
    pricing_id: Mapped[Optional[int]] = mapped_column(Integer)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True))
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)


    global_instruction: Mapped[Optional['GlobalInstruction']] = relationship('GlobalInstruction', back_populates='prompt_execution')
    pricing: Mapped[Optional['ModelPricing']] = relationship('ModelPricing', back_populates='prompt_execution')
    prompt_version: Mapped['PromptVersion'] = relationship('PromptVersion', back_populates='prompt_execution')
    section_instruction: Mapped[Optional['SectionInstruction']] = relationship('SectionInstruction', back_populates='prompt_execution')
    session: Mapped['ChatSession'] = relationship('ChatSession', back_populates='prompt_execution')
    model_output: Mapped[list['ModelOutput']] = relationship('ModelOutput', back_populates='prompt_execution')
