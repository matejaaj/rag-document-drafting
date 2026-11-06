from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import PrimaryKeyConstraint, TIMESTAMP, VARCHAR, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class DocumentType(Base):
    __tablename__ = 'document_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sys_c008225'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(1000), nullable=True)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True))

    prompt: Mapped[list['Prompt']] = relationship('Prompt', back_populates='document_type')
    template: Mapped[list['Template']] = relationship('Template', back_populates='document_type')
    chat_session: Mapped[list['ChatSession']] = relationship('ChatSession', back_populates='document_type')
