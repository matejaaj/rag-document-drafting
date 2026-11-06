from __future__ import annotations
from typing import Optional

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, VARCHAR, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class SessionSection(Base):
    __tablename__ = 'session_section'
    __table_args__ = (
        ForeignKeyConstraint(['session_id'], ['chat_session.id'], name='fk_session'),
        ForeignKeyConstraint(['template_section_id'], ['template_section.id'], name='fk_session_template_section'),
        PrimaryKeyConstraint('id', name='sys_c008253')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    template_section_id: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    position: Mapped[Optional[int]] = mapped_column(Integer)

    session: Mapped['ChatSession'] = relationship('ChatSession', back_populates='session_section')
    template_section: Mapped[Optional['TemplateSection']] = relationship('TemplateSection', back_populates='session_section')
    section_instruction: Mapped[list['SectionInstruction']] = relationship('SectionInstruction', back_populates='session_section')
    section_iteration: Mapped[list['SectionIteration']] = relationship('SectionIteration', back_populates='session_section')
