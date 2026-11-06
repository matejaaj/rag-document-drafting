from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime, timezone

from app.repository.base_repository import BaseRepository
from app.model.prompt.prompt_version import PromptVersion
from app.schema.prompt.prompt_version_schema import CreatePromptVersion

class PromptVersionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, PromptVersion)

    def find_by_name_and_prompt(self, name: str, prompt_id: int) -> Optional[PromptVersion]:
        with self.session_factory() as session:
            return (
                session.query(PromptVersion)
                .filter(
                    PromptVersion.name == name,
                    PromptVersion.prompt_id == prompt_id,
                    PromptVersion.deleted == 0,
                )
                .first()
            )

    def create(self, create_schema: CreatePromptVersion) -> PromptVersion:
        with self.session_factory() as session:
            prompt_version = PromptVersion(**create_schema.model_dump(exclude_unset=True))
            session.add(prompt_version)
            session.commit()
            session.refresh(prompt_version)
            return prompt_version

    def soft_delete_by_prompt(self, prompt_id: int) -> int:
        now = datetime.now(timezone.utc)
        with self.session_factory() as session:
            statement = (
                update(PromptVersion)
                .where(PromptVersion.prompt_id == prompt_id, PromptVersion.deleted == 0)
                .values(deleted=1, updated_at=now)
            )
            result = session.execute(statement)
            session.commit()
            return result.rowcount or 0
