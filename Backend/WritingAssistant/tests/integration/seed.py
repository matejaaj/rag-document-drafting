from datetime import datetime
from decimal import Decimal

from app.core.security import CurrentUser
from app.model import (
    ChatSession, DocumentType, ModelPricing, Prompt, PromptActiveHistory, PromptVersion, SessionSection, Template,
    TemplateSection,
)

WRITER = CurrentUser(id=1, email="pisac@ekolink.rs", role="EMPLOYEE")
OTHER_WRITER = CurrentUser(id=2, email="drugi.pisac@ekolink.rs", role="EMPLOYEE")
ADMIN = CurrentUser(id=3, email="admin@ekolink.rs", role="ADMIN")

SEEDED_AT = datetime(2025, 1, 1)


class Seed:
    def __init__(self):
        self.default_document_type = DocumentType(id=1, name="Default", created_at=SEEDED_AT, updated_at=SEEDED_AT)
        self.report_document_type = DocumentType(id=2, name="Izveštaj", created_at=SEEDED_AT, updated_at=SEEDED_AT)
        self.document_type_without_prompt = DocumentType(
            id=3, name="Zapisnik", created_at=SEEDED_AT, updated_at=SEEDED_AT
        )
        self.unused_document_type = DocumentType(id=4, name="Ugovor", created_at=SEEDED_AT, updated_at=SEEDED_AT)
        self.deleted_document_type = DocumentType(
            id=5, name="Ponuda", deleted=1, created_at=SEEDED_AT, updated_at=SEEDED_AT
        )

        self.test_model_pricing = ModelPricing(
            id=1, provider="test-provider", model="test-model", effective_from=SEEDED_AT,
            prompt_token_usd=Decimal("2"), completion_token_usd=Decimal("8"),
        )

        self.empty_template = Template(id=1, name="prazan", document_type_id=self.default_document_type.id)
        self.report_template = Template(
            id=2, name="Godišnji izveštaj", document_type_id=self.report_document_type.id, created_by=ADMIN.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        report_template_sections = [
            TemplateSection(id=1, template_id=self.report_template.id, name="Zaključak", position=2),
            TemplateSection(id=2, template_id=self.report_template.id, name="Uvod", position=0),
            TemplateSection(id=3, template_id=self.report_template.id, name="Rezultati", position=1),
        ]

        self.default_prompt = Prompt(
            id=1, title="Opšti prompt", document_type_id=self.default_document_type.id, created_by=ADMIN.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.report_prompt = Prompt(
            id=2, title="Prompt za izveštaje", document_type_id=self.report_document_type.id, created_by=ADMIN.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )

        self.active_default_version = PromptVersion(
            id=1, prompt_id=self.default_prompt.id, name="v1", prompt_text="Sekcija {CURRENT_SECTION_NAME}.",
            created_by=ADMIN.id, created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.active_report_version = PromptVersion(
            id=2, prompt_id=self.report_prompt.id, name="v1", prompt_text="Sekcija {CURRENT_SECTION_NAME} izveštaja.",
            created_by=ADMIN.id, created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.inactive_report_version = PromptVersion(
            id=3, prompt_id=self.report_prompt.id, name="v2", prompt_text="Sekcija {CURRENT_SECTION_NAME}, tri pasusa.",
            created_by=ADMIN.id, created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.default_activation = PromptActiveHistory(
            id=1, prompt_version_id=self.active_default_version.id,
            document_type_id=self.default_document_type.id, activated_by=ADMIN.id, activated_at=SEEDED_AT,
        )
        self.report_activation = PromptActiveHistory(
            id=2, prompt_version_id=self.active_report_version.id,
            document_type_id=self.report_document_type.id, activated_by=ADMIN.id, activated_at=SEEDED_AT,
        )

        self.writer_report_session = ChatSession(
            id=1, title="Godišnji izveštaj", template_id=self.empty_template.id,
            document_type_id=self.report_document_type.id, created_by=WRITER.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.writer_minutes_session = ChatSession(
            id=2, title="Zapisnik sa sastanka", template_id=self.empty_template.id,
            document_type_id=self.document_type_without_prompt.id, created_by=WRITER.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.other_writer_session = ChatSession(
            id=3, title="Tuđi izveštaj", template_id=self.empty_template.id,
            document_type_id=self.report_document_type.id, created_by=OTHER_WRITER.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.admin_test_session = ChatSession(
            id=4, title="Test verzije v2", template_id=self.empty_template.id,
            document_type_id=self.report_document_type.id, created_by=ADMIN.id,
            is_test_session=1, test_prompt_version_id=self.inactive_report_version.id,
            created_at=SEEDED_AT, updated_at=SEEDED_AT,
        )
        self.introduction_section = SessionSection(
            id=1, session_id=self.writer_report_session.id, name="Uvod", position=0
        )
        self.agenda_section = SessionSection(
            id=2, session_id=self.writer_minutes_session.id, name="Dnevni red", position=0
        )
        self.test_session_section = SessionSection(
            id=3, session_id=self.admin_test_session.id, name="Uvod", position=0
        )

        self.all = [
            self.default_document_type, self.report_document_type, self.document_type_without_prompt,
            self.unused_document_type, self.deleted_document_type,
            self.test_model_pricing,
            self.empty_template, self.report_template, *report_template_sections,
            self.default_prompt, self.report_prompt,
            self.active_default_version, self.active_report_version, self.inactive_report_version,
            self.default_activation, self.report_activation,
            self.writer_report_session, self.writer_minutes_session, self.other_writer_session,
            self.admin_test_session,
            self.introduction_section, self.agenda_section, self.test_session_section,
        ]
