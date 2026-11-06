from datetime import datetime, timezone
from typing import Optional

from app.schema.prompt.prompt_schema import (
    CreatePrompt, PromptOut, PromptWithActiveVersionOut,
    PromptWithActiveVersionPageOut, PromptQuery, PatchPromptTitle
)
from app.schema.common.pagination_schema import PaginationMeta
from app.schema.prompt.prompt_version_schema import PromptVersionOut
from app.repository.prompt.prompt_repository import PromptRepository
from app.repository.prompt.prompt_version_repository import PromptVersionRepository
from app.repository.prompt.prompt_active_history_repository import PromptActiveHistoryRepository
from app.services.document_type.document_type_service import DocumentTypeService
from app.model.prompt.prompt import Prompt
from app.core.exceptions import ConflictError, DuplicatedError


class PromptService:
    def __init__(
        self,
        prompt_repository: PromptRepository,
        prompt_version_repository: PromptVersionRepository,
        prompt_active_history_repository: PromptActiveHistoryRepository,
        document_type_service: DocumentTypeService,
    ):
        self.prompt_repository = prompt_repository
        self.prompt_version_repository = prompt_version_repository
        self.prompt_active_history_repository = prompt_active_history_repository
        self.document_type_service = document_type_service

    def add(self, create_schema: CreatePrompt, user_id: int) -> PromptOut:
        self.document_type_service.get(create_schema.document_type_id)

        now = datetime.now(timezone.utc)
        create_schema.created_by = user_id
        create_schema.created_at = now
        create_schema.updated_at = now
        create_schema.deleted = 0

        if self.prompt_repository.find_by_title_and_document_type(create_schema.title, create_schema.document_type_id):
            raise DuplicatedError(
                detail="Prompt sa tim nazivom već postoji za ovaj tip dokumenta"
            )
        prompt = self.prompt_repository.create_prompt(create_schema)

        return PromptOut(
            id=prompt.id,
            title=prompt.title,
            document_type_id=prompt.document_type_id,
            is_active=False,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )

    def list_with_active_versions(self, page: int, per_page: int, search_term: Optional[str] = None) -> PromptWithActiveVersionPageOut:
        term = (search_term or "").strip()

        if term:
            result = self.prompt_repository.search_by_term(term=term, page=page, per_page=per_page)
        else:
            query = PromptQuery(page=page, per_page=per_page, deleted=0)
            result = self.prompt_repository.read_page(query)

        prompts = result["items"]

        document_type_ids = {prompt.document_type_id for prompt in prompts}
        active_version_by_document_type = (
            self.prompt_active_history_repository.get_active_versions_by_document_type(document_type_ids)
        )

        items: list[PromptWithActiveVersionOut] = []
        for prompt in prompts:
            active_version = active_version_by_document_type.get(prompt.document_type_id)
            is_active = active_version is not None and active_version.prompt_id == prompt.id
            items.append(
                PromptWithActiveVersionOut(
                    id=prompt.id,
                    title=prompt.title,
                    document_type_id=prompt.document_type_id,
                    updated_at=prompt.updated_at,
                    is_active=is_active,
                    active_version=(
                        PromptVersionOut.model_validate(active_version).model_copy(update={"is_active": True})
                        if is_active
                        else None
                    ),
                )
            )

        return PromptWithActiveVersionPageOut(
            items=items,
            meta=PaginationMeta(**result["pagination"]),
        )

    def remove(self, prompt_id: int) -> None:
        prompt = self.prompt_repository.read_by_id(prompt_id, load_relationships=[Prompt.prompt_version])

        document_type = self.document_type_service.get_including_deleted(prompt.document_type_id)

        if document_type.name.strip().lower() == "default":
            active_version = self.prompt_active_history_repository.get_active_prompt_version(document_type.id)
            if active_version and active_version.prompt_id == prompt.id:
                raise ConflictError(
                    detail="Aktivan prompt tipa dokumenta Default ne može da se obriše"
                )

        self.prompt_version_repository.soft_delete_by_prompt(prompt_id)
        self.prompt_repository.delete_by_id(prompt_id)

    def update_title(self, prompt_id: int, title: str) -> PromptOut:
        self.prompt_repository.read_by_id(prompt_id)

        patch = PatchPromptTitle(
            title=title,
            updated_at=datetime.now(timezone.utc),
        )
        updated = self.prompt_repository.update(prompt_id, patch)

        return PromptOut(
            id=updated.id,
            title=updated.title,
            document_type_id=updated.document_type_id,
            is_active=False,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
