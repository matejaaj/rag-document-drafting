from __future__ import annotations
from typing import Optional
import datetime

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, TIMESTAMP, Text, text, Integer, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.base import Base


class OutputFeedback(Base):
    __tablename__ = 'output_feedback'
    __table_args__ = (
        CheckConstraint('rating_value BETWEEN 1 AND 5', name='chk_rating_value'),

        ForeignKeyConstraint(['model_output_id'], ['model_output.id'], name='fk_feedback_output'),
        PrimaryKeyConstraint('id', name='sys_c008281')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0 '))
    model_output_id: Mapped[Optional[int]] = mapped_column(Integer)
    rating_value: Mapped[Optional[int]] = mapped_column(Integer)
    comment_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP\n'))
    created_by_email: Mapped[Optional[str]] = mapped_column(VARCHAR(255))


    model_output: Mapped[Optional['ModelOutput']] = relationship('ModelOutput', back_populates='output_feedback')
