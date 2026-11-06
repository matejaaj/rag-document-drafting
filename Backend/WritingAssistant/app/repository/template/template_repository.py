from contextlib import AbstractContextManager
from typing import Callable, Optional, Sequence
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from app.repository.base_repository import BaseRepository
from app.model.template.template import Template
from app.model.template.template_section import TemplateSection
from app.model.document_type.document_type import DocumentType
from app.core.exceptions import NotFoundError


class TemplateRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, Template)

    def create_with_sections(
        self,
        *,
        name: str,
        document_type_id: int,
        storage_object_id: int,
        json_schema: Optional[str],
        created_by: int,
        section_names: Sequence[str],
        session: Session,
    ) -> Template:
        template = Template(
            name=name,
            document_type_id=document_type_id,
            storage_object_id=storage_object_id,
            json_schema=json_schema,
            created_by=created_by,
        )
        session.add(template)
        session.flush()
        for position, section_name in enumerate(section_names, start=1):
            session.add(
                TemplateSection(
                    template_id=template.id,
                    name=(section_name or f"Sekcija {position}")[:255],
                    position=position,
                )
            )
        return template

    def find_by_name(self, name: str) -> Template:
        with self.session_factory() as session:
            template = session.query(self.model).filter(
                self.model.name.ilike(name),
                self.model.deleted == 0
            ).first()
            if not template:
                raise NotFoundError(detail=f"Šablon '{name}' ne postoji")
            return template

    def search_by_term(self, term: str, page: int = 1, per_page: int = 20):
        pattern = f"%{term}%"

        with self.session_factory() as session:
            filtered_query = (
                session.query(self.model)
                .options(joinedload(self.model.document_type))
                .outerjoin(DocumentType, DocumentType.id == self.model.document_type_id)
                .filter(
                    self.model.deleted == 0,
                    or_(
                        self.model.name.ilike(pattern),
                        func.coalesce(DocumentType.name, "").ilike(pattern),
                    ),
                )
            )

            ordered_query = filtered_query.order_by(self.model.updated_at.desc())

            return self._page(filtered_query, ordered_query, page, per_page, "-updated_at")
