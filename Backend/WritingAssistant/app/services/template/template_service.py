from __future__ import annotations
from pathlib import Path
from typing import Optional
import json

from app.repository.template.template_repository import TemplateRepository
from app.schema.template.template_schema import (
    TemplateOut, TemplatePageOut, TemplateQuery, TemplateSectionOut, TemplateWithSectionsOut,
)
from app.schema.common.pagination_schema import PaginationMeta
from app.model.template.template import Template
from app.services.knowledge_base.storage_object_service import StorageObjectService
from app.services.template.template_parsers.registry import pick_template_parser
from app.core.exceptions import ValidationError, AuthError

TEMPLATE_STORAGE_DIR = Path("app/storage/templates")


class TemplateService:
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    def __init__(self, template_repository: TemplateRepository, storage_object_service: StorageObjectService):
        self.template_repository = template_repository
        self.storage_object_service = storage_object_service

    @staticmethod
    def _to_out(template: Template, document_type_name: Optional[str] = None) -> TemplateOut:
        return TemplateOut(
            id=template.id,
            name=template.name,
            document_type_id=template.document_type_id,
            document_type_name=document_type_name,
            updated_at=template.updated_at,
        )

    def get_with_sections(self, template_id: int) -> TemplateWithSectionsOut:
        template = self.template_repository.read_by_id(
            template_id, load_relationships=[Template.template_section]
        )
        return TemplateWithSectionsOut(
            id=template.id,
            name=template.name,
            document_type_id=template.document_type_id,
            sections=[TemplateSectionOut.model_validate(section) for section in template.template_section],
        )

    def get_by_name(self, name: str) -> TemplateOut:
        return self._to_out(self.template_repository.find_by_name(name))

    def list(self, page: int = 1, per_page: int = 20, search_term: Optional[str] = None) -> TemplatePageOut:
        term = (search_term or "").strip()

        if term:
            result = self.template_repository.search_by_term(term=term, page=page, per_page=per_page)
        else:
            query = TemplateQuery(page=page, per_page=per_page, deleted=0, ordering="-updated_at")
            result = self.template_repository.read_page(query, load_relationships=[Template.document_type])

        items = [
            self._to_out(
                template,
                document_type_name=template.document_type.name,
            )
            for template in result["items"]
        ]

        return TemplatePageOut(
            items=items,
            meta=PaginationMeta(**result["pagination"]),
        )

    def add_from_upload(
        self,
        *,
        name: str,
        document_type_id: int,
        filename: str,
        content: bytes,
        mime_type: str,
        created_by: int,
        repo_folder_id: Optional[int] = None,
    ) -> TemplateOut:

        if not content:
            raise ValidationError(detail="Fajl je prazan")

        if len(content) > self.MAX_FILE_SIZE_BYTES:
            raise ValidationError(detail="Fajl ne može biti veći od 5MB")

        try:
            parser = pick_template_parser(filename, mime_type)
        except ValueError as error:
            raise ValidationError(detail=str(error))
        parsed_template = parser.parse(content, filename)
        if not filename:
            raise ValidationError(detail="Nedostaje naziv fajla")

        with self.template_repository.transaction() as transaction:
            storage_object_id = self.storage_object_service.store_file(
                content=content,
                original_name=filename,
                mime_type=mime_type,
                storage_dir=TEMPLATE_STORAGE_DIR,
                created_by=created_by,
                repo_folder_id=repo_folder_id,
                session=transaction,
            )
            template = self.template_repository.create_with_sections(
                name=name,
                document_type_id=document_type_id,
                storage_object_id=storage_object_id,
                json_schema=(
                    json.dumps(parsed_template.json_schema, ensure_ascii=False)
                    if parsed_template.json_schema else None
                ),
                created_by=created_by,
                section_names=parsed_template.sections,
                session=transaction,
            )
            return self._to_out(template)

    def remove(self, template_id: int, user_id: int):
        template = self.template_repository.read_by_id(template_id)
        if template.created_by != user_id:
            raise AuthError(detail="Možeš da obrišeš samo svoj šablon")

        self.template_repository.delete_by_id(template_id)
