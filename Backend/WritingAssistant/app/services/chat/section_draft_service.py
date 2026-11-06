from app.repository.chat.section_draft_repository import SectionDraftRepository
from app.repository.chat.section_iteration_repository import SectionIterationRepository
from app.schema.chat.section_draft_schema import CreateSectionDraft
from app.schema.chat.section_iteration_schema import SectionIterationOut
from app.services.chat.section_iteration_service import SectionIterationService


class SectionDraftService:

    def __init__(
        self,
        section_draft_repository: SectionDraftRepository,
        section_iteration_repository: SectionIterationRepository,
        section_iteration_service: SectionIterationService,
    ):
        self.section_draft_repository = section_draft_repository
        self.section_iteration_repository = section_iteration_repository
        self.section_iteration_service = section_iteration_service

    def save_for_iteration(self, section_id: int, seq_no: int, content: str, user_id: int) -> SectionIterationOut:
        iteration = self.section_iteration_service.get_by_seq_no(section_id, seq_no, user_id)

        if iteration.section_draft:
            self.section_draft_repository.update_column(iteration.section_draft.id, "content", content)
        else:
            draft = self.section_draft_repository.create(
                CreateSectionDraft(
                    created_by=user_id,
                    content=content,
                    model_output=iteration.model_output.id if iteration.model_output else None,
                    deleted=0,
                )
            )
            self.section_iteration_repository.update_column(iteration.id, "section_draft_id", draft.id)

        return self.section_iteration_service.get_by_seq_no(section_id, seq_no, user_id)
