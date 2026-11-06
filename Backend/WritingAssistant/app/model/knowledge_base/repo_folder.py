from __future__ import annotations
import datetime
from typing import Optional
from sqlalchemy import Integer, VARCHAR, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base

class RepoFolder(Base):
    __tablename__ = "repo_folder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("repo_folder.id"))
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(True), server_default=text("CURRENT_TIMESTAMP"))
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0 "))

    parent: Mapped["RepoFolder"] = relationship("RepoFolder", remote_side=[id], backref="children")
