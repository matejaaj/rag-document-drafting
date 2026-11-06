from datetime import datetime, timezone

from typing import Optional

from app.services.llm.llm_service import LLMService
from app.services.llm.model_pricing_service import ModelPricingService
from app.services.prompt.prompt_version_service import PromptVersionService
from app.services.rag.retrieval_service import RetrievalService
from app.services.chat.prompt_composer import PromptComposer

from app.repository.chat.section_iteration_repository import SectionIterationRepository
from app.repository.chat.session_section_repository import SessionSectionRepository
from app.repository.chat.chat_session_repository import ChatSessionRepository
from app.repository.chat.global_instruction_repository import GlobalInstructionRepository
from app.repository.chat.section_instruction_repository import SectionInstructionRepository
from app.repository.chat.prompt_execution_repository import PromptExecutionRepository
from app.repository.chat.model_output_repository import ModelOutputRepository

from app.core.exceptions import AuthError, NotFoundError
from app.core.security import CurrentUser
from app.schema.chat.global_instruction_schema import CreateGlobalInstruction
from app.schema.chat.section_instruction_schema import CreateSectionInstruction, SectionInstructionOut
from app.schema.chat.prompt_execution_schema import CreatePromptExecution
from app.schema.chat.model_output_schema import CreateModelOutput
from app.schema.chat.section_iteration_schema import (
    CreateSectionIteration,
    GenerateIterationIn,
    ModelOutputOut,
    SectionIterationOut,
)
from app.schema.prompt.prompt_version_schema import PromptVersionOut

from app.model.chat.session_section import SessionSection
from app.model.chat.chat_session import ChatSession


class SectionIterationService:

    def __init__(
        self,
        section_iteration_repository: SectionIterationRepository,
        session_section_repository: SessionSectionRepository,
        chat_session_repository: ChatSessionRepository,
        global_instruction_repository: GlobalInstructionRepository,
        section_instruction_repository: SectionInstructionRepository,
        prompt_execution_repository: PromptExecutionRepository,
        model_output_repository: ModelOutputRepository,
        prompt_version_service: PromptVersionService,
        llm_service: LLMService,
        model_pricing_service: ModelPricingService,
        retrieval_service: RetrievalService,
        prompt_composer: PromptComposer,
    ):
        self.section_iteration_repository = section_iteration_repository
        self.session_section_repository = session_section_repository
        self.chat_session_repository = chat_session_repository
        self.global_instruction_repository = global_instruction_repository
        self.section_instruction_repository = section_instruction_repository
        self.prompt_execution_repository = prompt_execution_repository
        self.model_output_repository = model_output_repository
        self.prompt_version_service = prompt_version_service
        self.llm_service = llm_service
        self.model_pricing_service = model_pricing_service
        self.retrieval_service = retrieval_service
        self.prompt_composer = prompt_composer

    def _read_active_section(self, section_id: int) -> SessionSection:
        section = self.session_section_repository.read_by_id(section_id)
        if section.deleted == 1:
            raise NotFoundError(detail="Sekcija nije pronađena")
        return section

    def _assert_session_owner(self, chat_session: ChatSession, user_id: int) -> None:
        if chat_session.created_by != user_id:
            raise AuthError(detail="Nemaš pristup ovom dokumentu")

    def get_by_seq_no(self, section_id: int, seq_no: int, user_id: int) -> SectionIterationOut:
        section = self.session_section_repository.read_by_id(section_id, load_relationships=[SessionSection.session])
        self._assert_session_owner(section.session, user_id)
        if section.deleted == 1:
            raise NotFoundError(detail="Sekcija nije pronađena")

        iteration = self.section_iteration_repository.find_by_section_and_seq_no(section_id, seq_no)
        if not iteration:
            raise NotFoundError(detail="Iteracija nije pronađena")
        return SectionIterationOut.model_validate(iteration)

    def find_by_seq_no(self, section_id: int, seq_no: int) -> Optional[SectionIterationOut]:
        """No ownership check; callers must check access first."""
        iteration = self.section_iteration_repository.find_by_section_and_seq_no(section_id, seq_no)
        return SectionIterationOut.model_validate(iteration) if iteration else None

    def get_output_owner_id(self, model_output_id: int) -> int:
        model_output = self.model_output_repository.read_by_id(model_output_id)
        prompt_execution = self.prompt_execution_repository.read_by_id(model_output.prompt_execution_id)
        chat_session = self.chat_session_repository.read_by_id(prompt_execution.session_id)
        if model_output.deleted == 1 or prompt_execution.deleted == 1 or chat_session.deleted == 1:
            raise NotFoundError(detail="Generisani tekst nije pronađen")
        return chat_session.created_by

    def _resolve_prompt_version(self, chat_session: ChatSession, current_user: CurrentUser) -> PromptVersionOut:
        """Test sessions use their pinned version (admins only)."""
        if not chat_session.is_test_session:
            return self.prompt_version_service.resolve_active_for_document_type(chat_session.document_type_id)

        if current_user.role != "ADMIN":
            raise AuthError(detail="Samo admin može da koristi test sesiju")
        if not chat_session.test_prompt_version_id:
            raise NotFoundError(detail="Test sesija nema verziju prompta")
        return self.prompt_version_service.get_details(chat_session.test_prompt_version_id)

    def _compose_prompt(
        self, section: SessionSection, chat_session: ChatSession, prompt_version: PromptVersionOut,
        generate_request: GenerateIterationIn,
    ) -> str:
        retrieval_result = self.retrieval_service.retrieve_context(
            document_type_id=chat_session.document_type_id,
            global_instruction=generate_request.global_instruction or "",
            section_instruction=generate_request.section_instruction or "",
        )
        return self.prompt_composer.compose(
            section=section,
            session_sections=[session_section for session_section in chat_session.session_section if session_section.deleted == 0],
            prompt_template=prompt_version.prompt_text,
            global_instruction=generate_request.global_instruction,
            section_instruction=generate_request.section_instruction,
            rag_context=self.prompt_composer.build_rag_context(retrieval_result),
        )

    def _save_instructions(self, chat_session_id: int, section_id: int, generate_request: GenerateIterationIn):
        now = datetime.now(timezone.utc)
        global_text = (generate_request.global_instruction or "").strip()
        section_text = (generate_request.section_instruction or "").strip()
        global_instruction = section_instruction = None
        if global_text:
            global_instruction = self.global_instruction_repository.create(
                CreateGlobalInstruction(session_id=chat_session_id, text_=global_text, deleted=0, created_at=now)
            )
        if section_text:
            section_instruction = self.section_instruction_repository.create(
                CreateSectionInstruction(session_section_id=section_id, text_=section_text, deleted=0, created_at=now)
            )
        return global_instruction, section_instruction

    def generate(
        self, section_id: int, generate_request: GenerateIterationIn, current_user: CurrentUser
    ) -> SectionIterationOut:
        section = self._read_active_section(section_id)
        chat_session = self.chat_session_repository.read_by_id(
            section.session_id, load_relationships=[ChatSession.session_section]
        )
        self._assert_session_owner(chat_session, current_user.id)
        prompt_version = self._resolve_prompt_version(chat_session, current_user)
        final_prompt = self._compose_prompt(section, chat_session, prompt_version, generate_request)

        started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        llm_result = self.llm_service.generate(final_prompt)
        finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
        pricing_id, cost_usd = self.model_pricing_service.calculate_cost(llm_result, finished_at)
        global_instruction, section_instruction = self._save_instructions(chat_session.id, section_id, generate_request)

        prompt_execution = self.prompt_execution_repository.create(
            CreatePromptExecution(
                prompt_version_id=prompt_version.id,
                session_id=chat_session.id,
                status=llm_result.status,
                created_by=current_user.id,
                deleted=0,
                section_instruction_id=section_instruction.id if section_instruction else None,
                global_instruction_id=global_instruction.id if global_instruction else None,
                final_prompt=final_prompt,
                error_code=llm_result.error_code,
                error_message=llm_result.error_message,
                prompt_tokens=llm_result.prompt_tokens,
                output_tokens=llm_result.output_tokens,
                cost_usd=cost_usd or 0,
                started_at=started_at,
                finished_at=finished_at,
                pricing_id=pricing_id,
                duration_ms=int((finished_at - started_at).total_seconds() * 1000),
            )
        )
        model_output = self.model_output_repository.create(
            CreateModelOutput(prompt_execution_id=prompt_execution.id, generated_text=llm_result.generated_text)
        )
        iteration = self.section_iteration_repository.create(
            CreateSectionIteration(
                seq_no=self.section_iteration_repository.next_seq_no_for_section(section_id),
                session_id=chat_session.id,
                session_section_id=section_id,
                deleted=0,
                section_instruction_id=section_instruction.id if section_instruction else None,
                model_output_id=model_output.id,
            )
        )

        return SectionIterationOut(
            id=iteration.id,
            seq_no=iteration.seq_no,
            session_section_id=iteration.session_section_id,
            section_instruction=SectionInstructionOut.model_validate(section_instruction) if section_instruction else None,
            model_output=ModelOutputOut.model_validate(model_output),
        )
