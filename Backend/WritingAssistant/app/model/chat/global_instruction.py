from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, Text, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class GlobalInstruction(Base):
    __tablename__ = 'global_instruction'
    __table_args__ = (
        ForeignKeyConstraint(['session_id'], ['chat_session.id'], name='fk_global_instr'),
        PrimaryKeyConstraint('id', name='sys_c008261')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    text_: Mapped[Optional[str]] = mapped_column('text', Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP\n'))

    session: Mapped['ChatSession'] = relationship('ChatSession', back_populates='global_instruction')
    prompt_execution: Mapped[list['PromptExecution']] = relationship('PromptExecution', back_populates='global_instruction')
