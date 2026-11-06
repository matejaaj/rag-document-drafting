from contextlib import AbstractContextManager
from typing import Callable, Tuple, List, Dict
from sqlalchemy import func, and_
from sqlalchemy.orm import Session, joinedload
from app.model.chat.session_section import SessionSection
from app.model.chat.section_iteration import SectionIteration
from app.repository.base_repository import BaseRepository

class SessionSectionRepository(BaseRepository):
    DEFAULT_ORDERING = "position"

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, SessionSection)

    def list_with_latest_iteration(self, session_id: int) -> Tuple[List[SessionSection], Dict[int, SectionIteration]]:
        with self.session_factory() as session:
            sections = (
                session.query(SessionSection)
                .filter(SessionSection.session_id == session_id, SessionSection.deleted == 0)
                .order_by(SessionSection.position.asc(), SessionSection.id.asc())
                .all()
            )
            if not sections:
                return [], {}

            latest_seq_no_per_section = (
                session.query(
                    SectionIteration.session_section_id.label("section_id"),
                    func.max(SectionIteration.seq_no).label("max_seq_no"),
                )
                .filter(SectionIteration.session_id == session_id, SectionIteration.deleted == 0)
                .group_by(SectionIteration.session_section_id)
                .subquery()
            )

            latest_iterations = (
                session.query(SectionIteration)
                .join(
                    latest_seq_no_per_section,
                    and_(
                        SectionIteration.session_section_id == latest_seq_no_per_section.c.section_id,
                        SectionIteration.seq_no == latest_seq_no_per_section.c.max_seq_no,
                    ),
                )
                .filter(SectionIteration.deleted == 0)
                .options(
                    joinedload(SectionIteration.section_instruction),
                    joinedload(SectionIteration.model_output),
                    joinedload(SectionIteration.section_draft),
                )
                .all()
            )

            latest_iteration_by_section_id = {
                iteration.session_section_id: iteration for iteration in latest_iterations
            }
            return sections, latest_iteration_by_section_id
