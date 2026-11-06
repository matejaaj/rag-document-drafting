from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, Text, VARCHAR, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class Template(Base):
    __tablename__ = 'template'
    __table_args__ = (
        ForeignKeyConstraint(['document_type_id'], ['document_type.id'], name='fk_template_doc_type'),
        ForeignKeyConstraint(['storage_object_id'], ['storage_object.id'], name='fk_template_storage_object'),
        PrimaryKeyConstraint('id', name='sys_c008229')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    document_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    storage_object_id: Mapped[Optional[int]] = mapped_column(Integer)
    json_schema: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True))
    created_by: Mapped[Optional[int]] = mapped_column(Integer)

    document_type: Mapped['DocumentType'] = relationship('DocumentType', back_populates='template')
    storage_object: Mapped[Optional['StorageObject']] = relationship('StorageObject', back_populates='templates')
    chat_session: Mapped[list['ChatSession']] = relationship('ChatSession', back_populates='template')
    template_section: Mapped[list['TemplateSection']] = relationship('TemplateSection', back_populates='template')
