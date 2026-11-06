from datetime import datetime, timezone
from typing import Optional

from app.repository.feedback.output_feedback_repository import OutputFeedbackRepository
from app.services.chat.section_iteration_service import SectionIterationService

from app.schema.feedback.output_feedback_schema import (
    CreateOutputFeedback,
    OutputFeedbackOut,
    OutputFeedbackPage,
    OutputFeedbackItemOut,
)
from app.core.exceptions import NotFoundError, AuthError


class OutputFeedbackService:
    def __init__(
        self,
        output_feedback_repository: OutputFeedbackRepository,
        section_iteration_service: SectionIterationService,
    ):
        self.output_feedback_repository = output_feedback_repository
        self.section_iteration_service = section_iteration_service

    def add(self, create_schema: CreateOutputFeedback, user_id: int, user_email: Optional[str]) -> OutputFeedbackOut:
        output_owner_id = self.section_iteration_service.get_output_owner_id(create_schema.model_output_id)
        if output_owner_id != user_id:
            raise AuthError(detail="Možeš da oceniš samo tekst iz svog dokumenta")

        create_schema.created_by = user_id
        create_schema.created_by_email = user_email
        create_schema.created_at = datetime.now(timezone.utc)
        create_schema.deleted = 0

        feedback = self.output_feedback_repository.create_feedback(create_schema)
        return OutputFeedbackOut.model_validate(feedback)

    def list_for_prompt(self, prompt_id: int, page: int = 1, per_page: int = 5) -> OutputFeedbackPage:
        rows, pagination = self.output_feedback_repository.list_for_prompt(prompt_id, page=page, per_page=per_page)
        return OutputFeedbackPage(items=[OutputFeedbackItemOut(**row) for row in rows], meta=pagination)

    def list_for_version(self, version_id: int, page: int = 1, per_page: int = 5) -> OutputFeedbackPage:
        rows, pagination = self.output_feedback_repository.list_for_version(version_id, page=page, per_page=per_page)
        return OutputFeedbackPage(items=[OutputFeedbackItemOut(**row) for row in rows], meta=pagination)

    def get(self, feedback_id: int) -> OutputFeedbackItemOut:
        feedback = self.output_feedback_repository.find_details(feedback_id)
        if not feedback:
            raise NotFoundError(detail="Ocena nije pronađena")
        return OutputFeedbackItemOut(**feedback)
