from app.core.database import Database
from app.model import DocumentType, Template
from app.services.chat.chat_session_service import ChatSessionService
from app.services.prompt.prompt_version_service import PromptVersionService


def add_initial_data(database: Database) -> None:
    with database.session() as session:
        default_document_type = (
            session.query(DocumentType)
            .filter_by(name=PromptVersionService.DEFAULT_DOCUMENT_TYPE_NAME, deleted=0)
            .first()
        )
        if default_document_type is None:
            default_document_type = DocumentType(name=PromptVersionService.DEFAULT_DOCUMENT_TYPE_NAME, deleted=0)
            session.add(default_document_type)
            session.flush()

        empty_template = (
            session.query(Template)
            .filter_by(name=ChatSessionService.EMPTY_TEMPLATE_NAME, deleted=0)
            .first()
        )
        if empty_template is None:
            session.add(
                Template(
                    name=ChatSessionService.EMPTY_TEMPLATE_NAME,
                    document_type_id=default_document_type.id,
                    deleted=0,
                )
            )
        session.commit()
