from typing import Optional
from datetime import datetime, timezone

from app.repository.chat.chat_session_repository import ChatSessionRepository
from app.repository.chat.session_section_repository import SessionSectionRepository
from app.services.template.template_service import TemplateService
from app.services.document_type.document_type_service import DocumentTypeService
from app.services.prompt.prompt_version_service import PromptVersionService

from app.core.exceptions import AuthError

from app.schema.chat.chat_session_schema import (
    CreateChatSession,
    PatchChatSessionTitle,
    CreateTestChatSession,
    ChatSessionQuery,
    PatchChatSessionDocumentType,
    ChatSessionPageOut,
    ChatSessionOut,
)
from app.schema.common.pagination_schema import PaginationMeta
from app.schema.chat.session_section_schema import CreateSessionSection


class ChatSessionService:
    EMPTY_TEMPLATE_NAME = "prazan"

    def __init__(
        self,
        chat_session_repository: ChatSessionRepository,
        session_section_repository: SessionSectionRepository,
        template_service: TemplateService,
        document_type_service: DocumentTypeService,
        prompt_version_service: PromptVersionService,
    ):
        self.chat_session_repository = chat_session_repository
        self.session_section_repository = session_section_repository
        self.template_service = template_service
        self.document_type_service = document_type_service
        self.prompt_version_service = prompt_version_service

    def _read_owned(self, chat_session_id: int, user_id: int):
        chat_session = self.chat_session_repository.read_by_id(chat_session_id)
        if chat_session.created_by != user_id:
            raise AuthError(detail="Nemaš pristup ovom dokumentu")
        return chat_session

    def add(self, create_schema: CreateChatSession):
        now = datetime.now(timezone.utc)

        template = self.template_service.get_with_sections(create_schema.template_id)
        create_schema.document_type_id = template.document_type_id
        create_schema.title = create_schema.title or f"Novi Dokument {now.strftime('%Y-%m-%d %H:%M:%S')}"
        create_schema.deleted = 0
        create_schema.created_at = now
        create_schema.updated_at = now

        created = self.chat_session_repository.create(create_schema)

        if template.sections:
            ordered_sections = sorted(template.sections, key=lambda section: (section.position or 0, section.id))
            for template_section in ordered_sections:
                self.session_section_repository.create(
                    CreateSessionSection(
                        session_id=created.id,
                        template_section_id=template_section.id,
                        name=template_section.name,
                        position=template_section.position or 0,
                        deleted=0,
                    )
                )

        return ChatSessionOut.model_validate(created)

    def add_test(self, create_schema: CreateTestChatSession, user_id: int):
        now = datetime.now(timezone.utc)

        empty_template = self.template_service.get_by_name(self.EMPTY_TEMPLATE_NAME)
        prompt_version = self.prompt_version_service.get_details(create_schema.test_prompt_version_id)

        title = (
            create_schema.title
            or f"Test - {prompt_version.name} - {now.strftime('%Y-%m-%d')}"
        ).strip()

        test_session = CreateTestChatSession(
            template_id=empty_template.id,
            document_type_id=prompt_version.document_type_id,
            title=title,
            created_by=user_id,
            deleted=0,
            created_at=now,
            updated_at=now,
            is_test_session=1,
            test_prompt_version_id=prompt_version.id,
        )

        created = self.chat_session_repository.create(test_session)
        return ChatSessionOut.model_validate(created)

    def update_title(self, chat_session_id: int, title: str, user_id: int):
        self._read_owned(chat_session_id, user_id)

        patch = PatchChatSessionTitle(title=title, updated_at=datetime.now(timezone.utc))
        updated = self.chat_session_repository.update(chat_session_id, patch)
        return ChatSessionOut.model_validate(updated)

    def remove(self, chat_session_id: int, user_id: int):
        self._read_owned(chat_session_id, user_id)

        deleted = self.chat_session_repository.delete_by_id(chat_session_id)
        return ChatSessionOut.model_validate(deleted)

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> ChatSessionPageOut:
        term = (search_term or "").strip()

        if term:
            result = self.chat_session_repository.search_by_term(
                user_id=user_id, term=term, page=page, per_page=per_page
            )
        else:
            query = ChatSessionQuery(
                created_by=user_id,
                page=page,
                per_page=per_page,
                deleted=0,
                ordering="-updated_at",
            )
            result = self.chat_session_repository.read_page(query)

        return ChatSessionPageOut(
            items=[ChatSessionOut.model_validate(chat_session) for chat_session in result["items"]],
            meta=PaginationMeta(**result["pagination"]),
        )

    def update_document_type(self, chat_session_id: int, document_type_id: int, user_id: int):
        chat_session = self._read_owned(chat_session_id, user_id)

        if chat_session.is_test_session == 1:
            raise AuthError(detail="Test sesiji ne može da se menja tip dokumenta")

        self.document_type_service.get(document_type_id)

        patch = PatchChatSessionDocumentType(
            document_type_id=document_type_id,
            updated_at=datetime.now(timezone.utc),
        )

        updated = self.chat_session_repository.update(chat_session_id, patch)
        return ChatSessionOut.model_validate(updated)
