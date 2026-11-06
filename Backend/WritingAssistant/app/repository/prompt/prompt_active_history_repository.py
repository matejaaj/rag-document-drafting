from contextlib import AbstractContextManager
from typing import Callable, Dict, Iterable, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.prompt.prompt_active_history import PromptActiveHistory
from app.model.prompt.prompt_version import PromptVersion


class PromptActiveHistoryRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, PromptActiveHistory)

    def get_active_versions_by_document_type(
        self, document_type_ids: Iterable[int]
    ) -> Dict[int, PromptVersion]:
        unique_ids = list({document_type_id for document_type_id in document_type_ids if document_type_id is not None})
        if not unique_ids:
            return {}

        with self.session_factory() as session:

            activation_rank = func.row_number().over(
                partition_by=PromptActiveHistory.document_type_id,
                order_by=PromptActiveHistory.activated_at.desc(),
            ).label("activation_rank")

            ranked_activations = (
                session.query(
                    PromptActiveHistory.document_type_id.label("document_type_id"),
                    PromptActiveHistory.prompt_version_id.label("prompt_version_id"),
                    activation_rank,
                )
                .filter(
                    PromptActiveHistory.deleted == 0,
                    PromptActiveHistory.document_type_id.in_(unique_ids),
                )
                .subquery()
            )

            latest_activations = (
                session.query(ranked_activations.c.document_type_id, PromptVersion)
                .join(PromptVersion, PromptVersion.id == ranked_activations.c.prompt_version_id)
                .filter(
                    ranked_activations.c.activation_rank == 1,
                    PromptVersion.deleted == 0,
                )
                .all()
            )

            active_versions: Dict[int, PromptVersion] = {}
            for document_type_id, prompt_version in latest_activations:
                active_versions[document_type_id] = prompt_version

            return active_versions

    def get_active_prompt_version(self, document_type_id: int) -> Optional[PromptVersion]:
        with self.session_factory() as session:
            return (
                session.query(PromptVersion)
                .join(PromptActiveHistory, PromptActiveHistory.prompt_version_id == PromptVersion.id)
                .filter(
                    PromptActiveHistory.document_type_id == document_type_id,
                    PromptActiveHistory.deleted == 0,
                    PromptVersion.deleted == 0,
                )
                .order_by(PromptActiveHistory.activated_at.desc())
                .first()
            )
