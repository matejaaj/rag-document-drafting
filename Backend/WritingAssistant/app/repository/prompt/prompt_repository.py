from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.prompt.prompt import Prompt

from app.schema.prompt.prompt_schema import CreatePrompt

class PromptRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, Prompt)

    def find_by_title_and_document_type(self, title: str, document_type_id: int) -> Optional[Prompt]:
        with self.session_factory() as session:
            return (
                session.query(Prompt)
                .filter(
                    Prompt.title == title,
                    Prompt.document_type_id == document_type_id,
                    Prompt.deleted == 0,
                )
                .first()
            )

    def create_prompt(self, create_schema: CreatePrompt) -> Prompt:
        with self.session_factory() as session:
            prompt = Prompt(**create_schema.model_dump())
            session.add(prompt)
            session.commit()
            session.refresh(prompt)
            return prompt

    def search_by_term(self, term: str, page: int = 1, per_page: int = 20) -> dict:

        with self.session_factory() as session:
            filtered_query = (
                session.query(Prompt)
                .filter(
                    Prompt.deleted == 0,
                    func.lower(Prompt.title).like(f"%{term.lower()}%")
                )
            )

            ordered_query = filtered_query.order_by(Prompt.updated_at.desc())

            return self._page(filtered_query, ordered_query, page, per_page, "-updated_at")
