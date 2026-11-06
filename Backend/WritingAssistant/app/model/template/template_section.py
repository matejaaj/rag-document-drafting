from __future__ import annotations
from typing import Optional

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, VARCHAR, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class TemplateSection(Base):
    __tablename__ = 'template_section'
    __table_args__ = (
        ForeignKeyConstraint(['template_id'], ['template.id'], name='fk_template_section'),
        PrimaryKeyConstraint('id', name='sys_c008233')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    position: Mapped[Optional[int]] = mapped_column(Integer)

    template: Mapped['Template'] = relationship('Template', back_populates='template_section')
    session_section: Mapped[list['SessionSection']] = relationship('SessionSection', back_populates='template_section')
