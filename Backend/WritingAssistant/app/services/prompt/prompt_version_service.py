from datetime import datetime, timezone
from typing import Optional

from app.schema.prompt.prompt_version_schema import (
    CreatePromptVersion,
    PromptVersionOut,
    PromptVersionDetailsOut,
    PatchPromptVersionPromptText,
    PromptVersionPageOut,
    PromptVersionQuery,
    PatchPromptVersionBasicInfo,
)
from app.schema.common.pagination_schema import PaginationMeta
from app.schema.prompt.prompt_active_history_schema import CreatePromptActiveHistory

from app.repository.prompt.prompt_version_repository import PromptVersionRepository
from app.repository.prompt.prompt_repository import PromptRepository
from app.repository.prompt.prompt_active_history_repository import PromptActiveHistoryRepository
from app.services.document_type.document_type_service import DocumentTypeService
from app.core.exceptions import ConflictError, DuplicatedError, NotFoundError

from app.model.prompt.prompt_version import PromptVersion


class PromptVersionService:
    DEFAULT_DOCUMENT_TYPE_NAME = "Default"

    def __init__(
        self,
        prompt_version_repository: PromptVersionRepository,
        prompt_repository: PromptRepository,
        prompt_active_history_repository: PromptActiveHistoryRepository,
        document_type_service: DocumentTypeService,
    ):
        self.prompt_version_repository = prompt_version_repository
        self.prompt_repository = prompt_repository
        self.prompt_active_history_repository = prompt_active_history_repository
        self.document_type_service = document_type_service

    def get_details(self, version_id: int) -> PromptVersionDetailsOut:
        prompt_version = self.prompt_version_repository.read_by_id(
            version_id, load_relationships=[PromptVersion.prompt]
        )
        details = PromptVersionDetailsOut.model_validate(prompt_version)
        return details.model_copy(
            update={"document_type_id": prompt_version.prompt.document_type_id if prompt_version.prompt else None}
        )

    def find_active_for_document_type(self, document_type_id: int) -> Optional[PromptVersionOut]:
        prompt_version = self.prompt_active_history_repository.get_active_prompt_version(document_type_id)
        return PromptVersionOut.model_validate(prompt_version) if prompt_version else None

    def resolve_active_for_document_type(self, document_type_id: int) -> PromptVersionOut:
        """Falls back to the active version of the Default document type."""
        document_type = self.document_type_service.get_including_deleted(document_type_id)
        active_version = None if document_type.deleted == 1 else self.find_active_for_document_type(document_type_id)
        if active_version is None:
            default_document_type = self.document_type_service.find_active_by_name(self.DEFAULT_DOCUMENT_TYPE_NAME)
            if not default_document_type:
                raise NotFoundError(detail='Ne postoji tip dokumenta "Default"')
            active_version = self.find_active_for_document_type(default_document_type.id)
        if not active_version:
            raise NotFoundError(detail="Tip dokumenta nema aktivnu verziju prompta")
        return active_version

    def add(self, create_schema: CreatePromptVersion, user_id: int) -> PromptVersionOut:
        self.prompt_repository.read_by_id(create_schema.prompt_id)
        now = datetime.now(timezone.utc)
        create_schema.created_by = user_id
        create_schema.created_at = now
        create_schema.updated_at = now
        create_schema.deleted = 0
        if self.prompt_version_repository.find_by_name_and_prompt(create_schema.name, create_schema.prompt_id):
            raise DuplicatedError(detail="Verzija sa tim nazivom već postoji za ovaj prompt")
        prompt_version = self.prompt_version_repository.create(create_schema)
        return PromptVersionOut.model_validate(prompt_version)

    def activate(self, version_id: int, user_id: int) -> PromptVersionOut:
        prompt_version = self.prompt_version_repository.read_by_id(
            version_id, load_relationships=[PromptVersion.prompt]
        )
        now = datetime.now(timezone.utc)
        self.prompt_active_history_repository.create(
            CreatePromptActiveHistory(
                prompt_version_id=prompt_version.id,
                document_type_id=prompt_version.prompt.document_type_id,
                activated_by=user_id,
                activated_at=now,
                deleted=0,
            )
        )
        activated = PromptVersionOut.model_validate(prompt_version)
        return activated.model_copy(update={"is_active": True})

    def list_for_prompt(
        self, prompt_id: int, page: int = 1, per_page: int = 20
    ) -> PromptVersionPageOut:
        prompt = self.prompt_repository.read_by_id(prompt_id)
        active_version_by_document_type = self.prompt_active_history_repository.get_active_versions_by_document_type(
            [prompt.document_type_id]
        )
        active_version = active_version_by_document_type.get(prompt.document_type_id)
        active_version_id = active_version.id if active_version else None
        query = PromptVersionQuery(
            page=page,
            per_page=per_page,
            prompt_id=prompt_id,
            deleted=0,
        )
        result = self.prompt_version_repository.read_page(query)
        items = [
            PromptVersionOut.model_validate(prompt_version).model_copy(
                update={"is_active": (prompt_version.id == active_version_id)}
            )
            for prompt_version in result["items"]
        ]
        return PromptVersionPageOut(
            items=items,
            meta=PaginationMeta(**result["pagination"]),
        )

    def remove(self, version_id: int) -> None:
        prompt_version = self.prompt_version_repository.read_by_id(
            version_id, load_relationships=[PromptVersion.prompt]
        )
        active_version = self.prompt_active_history_repository.get_active_prompt_version(
            prompt_version.prompt.document_type_id
        )
        if active_version is not None and active_version.id == prompt_version.id:
            raise ConflictError(
                detail=(
                    "Ne možeš obrisati aktivnu verziju. "
                    "Postavi neku drugu verziju kao aktivnu i pokušaj ponovo."
                )
            )
        self.prompt_version_repository.delete_by_id(version_id)

    def update_basic_info(
        self, version_id: int, patch_schema: PatchPromptVersionBasicInfo
    ) -> PromptVersionOut:
        patch_schema.updated_at = datetime.now(timezone.utc)
        updated = self.prompt_version_repository.update(version_id, patch_schema)
        return PromptVersionOut.model_validate(updated)

    def update_prompt_text(
        self, version_id: int, patch_schema: PatchPromptVersionPromptText
    ) -> PromptVersionOut:
        patch_schema.updated_at = datetime.now(timezone.utc)
        updated = self.prompt_version_repository.update(version_id, patch_schema)
        return PromptVersionOut.model_validate(updated)
