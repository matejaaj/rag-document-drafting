from typing import Optional
from datetime import datetime, timezone

from app.repository.document_type.document_type_repository import DocumentTypeRepository
from app.model.document_type.document_type import DocumentType

from app.schema.document_type.document_type_schema import (
    CreateDocumentType,
    DocumentTypeOut,
    DocumentTypeQuery,
    DocumentTypePageOut,
    UpdateDocumentType,
)
from app.schema.common.pagination_schema import PaginationMeta
from app.core.exceptions import ConflictError, DuplicatedError, NotFoundError


class DocumentTypeService:
    def __init__(self, document_type_repository: DocumentTypeRepository):
        self.document_type_repository = document_type_repository

    def _assert_not_default(self, document_type: DocumentType):
        if document_type.name and document_type.name.lower() == "default":
            raise ConflictError(detail='Tip dokumenta "Default" ne može da se menja ni briše')

    def list(self, page: int, per_page: int, name: Optional[str] = None, ordering: str = "-updated_at") -> DocumentTypePageOut:
        query = DocumentTypeQuery(page=page, per_page=per_page, name=name, deleted=0, ordering=ordering)
        result = self.document_type_repository.read_page(query)
        items = [DocumentTypeOut.model_validate(document_type) for document_type in result["items"]]
        return DocumentTypePageOut(
            items=items,
            meta=PaginationMeta(**result["pagination"]),
        )

    def get(self, id: int) -> DocumentTypeOut:
        document_type = self.document_type_repository.read_by_id(id)
        return DocumentTypeOut.model_validate(document_type)

    def add(self, create_schema: CreateDocumentType) -> DocumentTypeOut:
        now = datetime.now(timezone.utc)
        create_schema.created_at = now
        create_schema.updated_at = now

        existing = self.document_type_repository.find_by_name_including_deleted(create_schema.name)
        if existing:
            if existing.deleted == 1:
                existing.deleted = 0
                existing.updated_at = now
                restored = self.document_type_repository.save(existing)
                return DocumentTypeOut.model_validate(restored)
            raise DuplicatedError(detail="Tip dokumenta sa tim nazivom već postoji")

        created = self.document_type_repository.create(create_schema)
        return DocumentTypeOut.model_validate(created)

    def update(self, id: int, update_schema: UpdateDocumentType) -> DocumentTypeOut:
        document_type = self.document_type_repository.read_by_id(id)
        self._assert_not_default(document_type)

        if update_schema.name:
            duplicate = self.document_type_repository.find_active_duplicate(update_schema.name, exclude_id=id)
            if duplicate:
                raise DuplicatedError(detail="Tip dokumenta sa tim nazivom već postoji")

        document_type.name = update_schema.name or document_type.name
        document_type.description = (
            update_schema.description if update_schema.description is not None else document_type.description
        )
        updated = self.document_type_repository.save(document_type)

        return DocumentTypeOut.model_validate(updated)

    def remove(self, id: int) -> None:
        document_type = self.document_type_repository.find_by_id_including_deleted(id)
        if not document_type:
            raise NotFoundError(detail=f"Tip dokumenta {id} ne postoji")

        self._assert_not_default(document_type)

        if self.document_type_repository.has_active_dependents(id):
            raise ConflictError(
                detail="Tip dokumenta se koristi, pa ne može da se obriše"
            )

        document_type.deleted = 1
        self.document_type_repository.save(document_type)

    def get_including_deleted(self, id: int) -> DocumentTypeOut:
        document_type = self.document_type_repository.read_by_id_including_deleted(id)
        return DocumentTypeOut.model_validate(document_type)

    def find_active_by_name(self, name: str) -> Optional[DocumentTypeOut]:
        document_type = self.document_type_repository.find_active_by_name(name)
        return DocumentTypeOut.model_validate(document_type) if document_type else None
