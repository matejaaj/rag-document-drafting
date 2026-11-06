from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.repository.base_repository import BaseRepository
from app.model.document_type.document_type import DocumentType
from app.model.prompt.prompt import Prompt
from app.model.chat.chat_session import ChatSession
from app.core.exceptions import NotFoundError
from app.schema.document_type.document_type_schema import CreateDocumentType

class DocumentTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, DocumentType)

    def find_by_id_including_deleted(self, id: int) -> Optional[DocumentType]:
        with self.session_factory() as session:
            return session.query(DocumentType).filter(DocumentType.id == id).first()

    def read_by_id_including_deleted(self, id: int) -> DocumentType:
        document_type = self.find_by_id_including_deleted(id)
        if not document_type:
            raise NotFoundError(detail=f"Tip dokumenta {id} ne postoji")
        return document_type

    def has_active_dependents(self, id: int) -> bool:
        with self.session_factory() as session:
            prompt_count = (
                session.query(Prompt)
                .filter(Prompt.document_type_id == id, Prompt.deleted == 0)
                .count()
            )
            chat_session_count = (
                session.query(ChatSession)
                .filter(ChatSession.document_type_id == id, ChatSession.deleted == 0)
                .count()
            )
            return (prompt_count + chat_session_count) > 0

    def find_active_by_name(self, name: str) -> Optional[DocumentType]:
        with self.session_factory() as session:
            return (
                session.query(DocumentType)
                .filter(func.lower(DocumentType.name) == func.lower(name),
                        DocumentType.deleted == 0)
                .first()
            )

    def find_by_name_including_deleted(self, name: str) -> Optional[DocumentType]:
        with self.session_factory() as session:
            return (
                session.query(DocumentType)
                .filter(func.lower(DocumentType.name) == func.lower(name))
                .first()
            )

    def find_active_duplicate(self, name: str, exclude_id: Optional[int] = None) -> Optional[DocumentType]:
        with self.session_factory() as session:
            query = session.query(DocumentType).filter(
                func.lower(DocumentType.name) == func.lower(name),
                DocumentType.deleted == 0,
            )
            if exclude_id:
                query = query.filter(DocumentType.id != exclude_id)
            return query.first()

    def create(self, create_schema: CreateDocumentType) -> DocumentType:
        with self.session_factory() as session:
            document_type = DocumentType(**create_schema.model_dump(exclude_none=True))
            session.add(document_type)
            session.commit()
            session.refresh(document_type)
            return document_type

    def save(self, document_type: DocumentType) -> DocumentType:
        with self.session_factory() as session:
            document_type.updated_at = func.current_timestamp()
            session.add(document_type)
            session.commit()
            session.refresh(document_type)
            return document_type
