from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlalchemy.orm import Session, joinedload
from app.repository.base_repository import BaseRepository
from app.model.chat.section_iteration import SectionIteration
from sqlalchemy import func

class SectionIterationRepository(BaseRepository):
    DEFAULT_ORDERING = "-seq_no"

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, SectionIteration)

    def find_by_section_and_seq_no(self, section_id: int, seq_no: int) -> Optional[SectionIteration]:
        with self.session_factory() as session:
            iteration = (
                session.query(SectionIteration)
                .filter(
                    SectionIteration.session_section_id == section_id,
                    SectionIteration.seq_no == seq_no,
                    SectionIteration.deleted == 0,
                )
                .options(
                    joinedload(SectionIteration.section_instruction),
                    joinedload(SectionIteration.model_output),
                    joinedload(SectionIteration.section_draft),
                )
                .first()
            )
            if iteration:
                session.refresh(iteration)
                session.expunge(iteration)
            return iteration

    def next_seq_no_for_section(self, section_id: int) -> int:
        with self.session_factory() as session:
            max_seq_no = session.query(func.max(SectionIteration.seq_no)).filter(
                SectionIteration.session_section_id == section_id
            ).scalar()
            return (max_seq_no or 0) + 1
