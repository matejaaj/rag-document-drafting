from typing import List
from datetime import datetime, timezone

from app.repository.chat.session_section_repository import SessionSectionRepository
from app.repository.chat.chat_session_repository import ChatSessionRepository
from app.repository.chat.global_instruction_repository import GlobalInstructionRepository
from app.core.exceptions import AuthError
from app.schema.chat.session_overview_schema import SessionSectionWithLatestOut, SessionOverviewOut
from app.schema.chat.section_iteration_schema import SectionIterationOut, SectionInstructionOut, ModelOutputOut
from app.schema.chat.session_section_schema import CreateSessionSection, PatchSessionSectionTitle, SessionSectionOut
from app.schema.chat.section_draft_schema import SectionDraftOut
from app.model.chat.session_section import SessionSection
from app.model.chat.section_iteration import SectionIteration


class SessionSectionService:
    def __init__(
        self,
        session_section_repository: SessionSectionRepository,
        chat_session_repository: ChatSessionRepository,
        global_instruction_repository: GlobalInstructionRepository,
    ):
        self.session_section_repository = session_section_repository
        self.chat_session_repository = chat_session_repository
        self.global_instruction_repository = global_instruction_repository

    def add(self, create_schema: CreateSessionSection) -> SessionSectionOut:
        return SessionSectionOut.model_validate(self.session_section_repository.create(create_schema))

    def remove(self, id: int, user_id: int):
        section = self.session_section_repository.read_by_id(id)
        chat_session = self.chat_session_repository.read_by_id(section.session_id)

        if chat_session.created_by != user_id:
            raise AuthError(detail="Nemaš pristup ovom dokumentu")

        self.session_section_repository.delete_by_id(id)

    def update_title(self, session_section_id: int, name: str, user_id: int):
        section = self.session_section_repository.read_by_id(
            session_section_id, load_relationships=[SessionSection.session]
        )
        if section.session.created_by != user_id:
            raise AuthError(detail="Nemaš pristup ovom dokumentu")

        patch = PatchSessionSectionTitle(name=name, updated_at=datetime.now(timezone.utc))
        return SessionSectionOut.model_validate(self.session_section_repository.update(session_section_id, patch))

    @staticmethod
    def _to_iteration_out(iteration: SectionIteration) -> SectionIterationOut:
        return SectionIterationOut(
            id=iteration.id,
            seq_no=iteration.seq_no,
            session_section_id=iteration.session_section_id,
            section_instruction=(
                SectionInstructionOut.model_validate(iteration.section_instruction)
                if iteration.section_instruction and iteration.section_instruction.deleted == 0
                else None
            ),
            model_output=(
                ModelOutputOut.model_validate(iteration.model_output)
                if iteration.model_output and iteration.model_output.deleted == 0
                else None
            ),
            section_draft=(
                SectionDraftOut.model_validate(iteration.section_draft)
                if iteration.section_draft and iteration.section_draft.deleted == 0
                else None
            ),
        )

    def get_session_overview(self, session_id: int, user_id: int) -> SessionOverviewOut:
        chat_session = self.chat_session_repository.read_by_id(session_id)
        if chat_session.created_by != user_id:
            raise AuthError(detail="Nemaš pristup ovom dokumentu")

        sections, latest_iteration_by_section_id = self.session_section_repository.list_with_latest_iteration(session_id)
        global_instruction = self.global_instruction_repository.find_latest_for_session(session_id)
        global_instruction_text = (
            global_instruction.text_ if global_instruction else ""
        )

        section_overviews: List[SessionSectionWithLatestOut] = []
        for section in sections:
            latest_iteration = latest_iteration_by_section_id.get(section.id)
            section_overviews.append(
                SessionSectionWithLatestOut(
                    id=section.id,
                    session_id=section.session_id,
                    name=section.name,
                    position=section.position,
                    latest_iteration=self._to_iteration_out(latest_iteration) if latest_iteration else None,
                )
            )

        return SessionOverviewOut(
            document_type_id=chat_session.document_type_id,
            title=chat_session.title,
            latest_global_instruction_text=global_instruction_text,
            sections=section_overviews,
        )
