from __future__ import annotations
from typing import Optional, List
import datetime
from sqlalchemy import Integer, VARCHAR, TIMESTAMP, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base

class StorageObject(Base):
    __tablename__ = "storage_object"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    original_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0 "))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(True), server_default=text("CURRENT_TIMESTAMP"))
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    repo_folder_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("repo_folder.id"))

    repo_folder = relationship("RepoFolder", backref="storage_objects")
    templates: Mapped[List["Template"]] = relationship("Template", back_populates="storage_object")
