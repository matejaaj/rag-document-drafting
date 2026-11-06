from contextlib import AbstractContextManager
from typing import Callable, Tuple, List, Dict, Any, Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc

from app.repository.base_repository import BaseRepository
from app.model.feedback.output_feedback import OutputFeedback
from app.model.chat.model_output import ModelOutput
from app.model.chat.prompt_execution import PromptExecution
from app.model.prompt.prompt_version import PromptVersion
from app.model.prompt.prompt import Prompt
from app.schema.feedback.output_feedback_schema import CreateOutputFeedback


class OutputFeedbackRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, OutputFeedback)

    def _normalize_paging(self, page: Optional[int], per_page: Optional[int]) -> Tuple[int, int]:
        page_number = page or 1
        page_size = per_page or 5
        return (max(1, page_number), max(1, page_size))

    def _active_feedback_query(self, session: Session):
        model_output = aliased(ModelOutput)
        prompt_execution = aliased(PromptExecution)
        prompt_version = aliased(PromptVersion)
        prompt = aliased(Prompt)

        query = (
            session.query(
                OutputFeedback.id.label("id"),
                OutputFeedback.rating_value.label("rating_value"),
                OutputFeedback.comment_text.label("comment_text"),
                OutputFeedback.created_at.label("created_at"),
                OutputFeedback.created_by.label("created_by"),
                OutputFeedback.created_by_email.label("created_by_email"),
            )
            .join(model_output, model_output.id == OutputFeedback.model_output_id)
            .join(prompt_execution, prompt_execution.id == model_output.prompt_execution_id)
            .join(prompt_version, prompt_version.id == prompt_execution.prompt_version_id)
            .join(prompt, prompt.id == prompt_version.prompt_id)
            .filter(
                OutputFeedback.deleted == 0,
                model_output.deleted == 0,
                prompt_execution.deleted == 0,
                prompt_version.deleted == 0,
                prompt.deleted == 0,
            )
            .order_by(desc(OutputFeedback.created_at), desc(OutputFeedback.id))
        )
        return query, prompt_version, prompt

    def _feedback_details_query(self, session: Session):
        model_output = aliased(ModelOutput)
        prompt_execution = aliased(PromptExecution)
        prompt_version = aliased(PromptVersion)
        prompt = aliased(Prompt)

        return (
            session.query(
                OutputFeedback.id.label("id"),
                OutputFeedback.rating_value.label("rating_value"),
                OutputFeedback.comment_text.label("comment_text"),
                OutputFeedback.created_at.label("created_at"),
                OutputFeedback.created_by.label("created_by"),
                OutputFeedback.created_by_email.label("created_by_email"),
                prompt_execution.final_prompt.label("final_prompt"),
                model_output.generated_text.label("generated_text"),
            )
            .join(model_output, model_output.id == OutputFeedback.model_output_id)
            .join(prompt_execution, prompt_execution.id == model_output.prompt_execution_id)
            .join(prompt_version, prompt_version.id == prompt_execution.prompt_version_id)
            .join(prompt, prompt.id == prompt_version.prompt_id)
            .filter(
                OutputFeedback.deleted == 0,
                model_output.deleted == 0,
                prompt_execution.deleted == 0,
                prompt_version.deleted == 0,
                prompt.deleted == 0,
            )
        )

    def list_for_prompt(self, prompt_id: int, page: int = 1, per_page: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        with self.session_factory() as session:
            query, prompt_version, prompt = self._active_feedback_query(session)
            query = query.filter(prompt.id == prompt_id)
            total_count = query.count()
            page, per_page = self._normalize_paging(page, per_page)
            rows = query.limit(per_page).offset((page - 1) * per_page).all()
            items = [dict(row._mapping) for row in rows]
            return items, {"page": page, "per_page": per_page, "total_count": total_count}

    def list_for_version(self, version_id: int, page: int = 1, per_page: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        with self.session_factory() as session:
            query, prompt_version, prompt = self._active_feedback_query(session)
            query = query.filter(prompt_version.id == version_id)
            total_count = query.count()
            page, per_page = self._normalize_paging(page, per_page)
            rows = query.limit(per_page).offset((page - 1) * per_page).all()
            items = [dict(row._mapping) for row in rows]
            return items, {"page": page, "per_page": per_page, "total_count": total_count}

    def find_details(self, feedback_id: int) -> Optional[Dict[str, Any]]:
        with self.session_factory() as session:
            row = self._feedback_details_query(session).filter(OutputFeedback.id == feedback_id).first()
            if not row:
                return None
            feedback = dict(row._mapping)
            feedback["details"] = {
                "final_prompt": feedback.pop("final_prompt", None),
                "generated_text": feedback.pop("generated_text", None),
            }
            return feedback

    def create_feedback(self, create_schema: CreateOutputFeedback) -> OutputFeedback:
        with self.session_factory() as session:
            feedback = OutputFeedback(**create_schema.model_dump())
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return feedback
