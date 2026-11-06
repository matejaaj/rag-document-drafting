from dependency_injector import containers, providers

from app.core.database import Database

from app.repository.analytics.analytics_repository import AnalyticsRepository
from app.repository.chat.chat_session_repository import ChatSessionRepository
from app.repository.chat.global_instruction_repository import GlobalInstructionRepository
from app.repository.chat.model_output_repository import ModelOutputRepository
from app.repository.chat.prompt_execution_repository import PromptExecutionRepository
from app.repository.chat.section_draft_repository import SectionDraftRepository
from app.repository.chat.section_instruction_repository import SectionInstructionRepository
from app.repository.chat.section_iteration_repository import SectionIterationRepository
from app.repository.chat.session_section_repository import SessionSectionRepository
from app.repository.document_type.document_type_repository import DocumentTypeRepository
from app.repository.feedback.output_feedback_repository import OutputFeedbackRepository
from app.repository.knowledge_base.repo_folder_repository import RepoFolderRepository
from app.repository.knowledge_base.storage_object_repository import StorageObjectRepository
from app.repository.llm.model_pricing_repository import ModelPricingRepository
from app.repository.prompt.prompt_active_history_repository import PromptActiveHistoryRepository
from app.repository.prompt.prompt_repository import PromptRepository
from app.repository.prompt.prompt_version_repository import PromptVersionRepository
from app.repository.rag.vector_repository import VectorRepository
from app.repository.template.template_repository import TemplateRepository

from app.services.analytics.analytics_service import AnalyticsService
from app.services.analytics.report.document_type_report_renderer import DocumentTypeReportHtmlRenderer
from app.services.analytics.report.document_type_report_service import DocumentTypeReportService
from app.services.analytics.report.document_report_renderer import DocumentReportHtmlRenderer
from app.services.analytics.report.document_report_service import DocumentReportService
from app.services.analytics.report.xhtml2pdf_engine import Xhtml2PdfEngine
from app.services.chat.chat_session_service import ChatSessionService
from app.services.chat.prompt_composer import PromptComposer
from app.services.chat.section_draft_service import SectionDraftService
from app.services.chat.section_iteration_service import SectionIterationService
from app.services.chat.session_section_service import SessionSectionService
from app.services.document_type.document_type_service import DocumentTypeService
from app.services.feedback.output_feedback_service import OutputFeedbackService
from app.services.knowledge_base.repo_folder_service import RepoFolderService
from app.services.knowledge_base.storage_object_service import StorageObjectService
from app.services.llm.llm_client.openai_client import OpenAIClient
from app.services.llm.llm_service import LLMService
from app.services.llm.model_pricing_service import ModelPricingService
from app.services.prompt.prompt_service import PromptService
from app.services.prompt.prompt_version_service import PromptVersionService
from app.services.rag.chunking_service import ChunkingService
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.retrieval_service import RetrievalService
from app.services.rag.summarization_service import SummarizationService
from app.services.rag.vector_ingestion_service import VectorIngestionService
from app.services.rag.vector_service import VectorService
from app.services.template.template_service import TemplateService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.analytics.analytics",
            "app.api.v1.endpoints.analytics.report",
            "app.api.v1.endpoints.chat.chat_session",
            "app.api.v1.endpoints.chat.session_section",
            "app.api.v1.endpoints.document_type.document_type",
            "app.api.v1.endpoints.feedback.output_feedback",
            "app.api.v1.endpoints.knowledge_base.repo_folder",
            "app.api.v1.endpoints.knowledge_base.storage_object",
            "app.api.v1.endpoints.prompt.prompt",
            "app.api.v1.endpoints.prompt.prompt_version",
            "app.api.v1.endpoints.template.template",
        ]
    )

    database = providers.Singleton(Database)

    llm_client = providers.Singleton(OpenAIClient)
    llm_service = providers.Singleton(LLMService, llm_client=llm_client)

    model_pricing_repository = providers.Factory(ModelPricingRepository, session_factory=database.provided.session)
    model_pricing_service = providers.Factory(
        ModelPricingService,
        model_pricing_repository=model_pricing_repository,
        llm_service=llm_service,
    )

    vector_repository = providers.Singleton(VectorRepository)
    vector_service = providers.Factory(VectorService, vector_repository=vector_repository)
    embedding_service = providers.Singleton(EmbeddingService)
    chunking_service = providers.Singleton(
        ChunkingService,
        max_model_tokens=512,
        target_tokens=360,
        overlap_tokens=64,
    )
    summarization_service = providers.Factory(SummarizationService, llm_service=llm_service)
    vector_ingestion_service = providers.Factory(
        VectorIngestionService,
        vector_service=vector_service,
        summarization_service=summarization_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
    )
    retrieval_service = providers.Singleton(
        RetrievalService,
        embedding_service=embedding_service,
        vector_service=vector_service,
    )

    document_type_repository = providers.Factory(DocumentTypeRepository, session_factory=database.provided.session)
    document_type_service = providers.Factory(
        DocumentTypeService,
        document_type_repository=document_type_repository,
    )

    storage_object_repository = providers.Factory(StorageObjectRepository, session_factory=database.provided.session)
    repo_folder_repository = providers.Factory(RepoFolderRepository, session_factory=database.provided.session)
    storage_object_service = providers.Factory(
        StorageObjectService,
        storage_object_repository=storage_object_repository,
        vector_ingestion_service=vector_ingestion_service,
        vector_service=vector_service,
    )
    repo_folder_service = providers.Factory(
        RepoFolderService,
        repo_folder_repository=repo_folder_repository,
    )

    template_repository = providers.Factory(TemplateRepository, session_factory=database.provided.session)
    template_service = providers.Factory(
        TemplateService,
        template_repository=template_repository,
        storage_object_service=storage_object_service,
    )

    prompt_repository = providers.Factory(PromptRepository, session_factory=database.provided.session)
    prompt_version_repository = providers.Factory(PromptVersionRepository, session_factory=database.provided.session)
    prompt_active_history_repository = providers.Factory(PromptActiveHistoryRepository, session_factory=database.provided.session)
    prompt_service = providers.Factory(
        PromptService,
        prompt_repository=prompt_repository,
        prompt_version_repository=prompt_version_repository,
        prompt_active_history_repository=prompt_active_history_repository,
        document_type_service=document_type_service,
    )
    prompt_version_service = providers.Factory(
        PromptVersionService,
        prompt_version_repository=prompt_version_repository,
        prompt_repository=prompt_repository,
        prompt_active_history_repository=prompt_active_history_repository,
        document_type_service=document_type_service,
    )

    chat_session_repository = providers.Factory(ChatSessionRepository, session_factory=database.provided.session)
    session_section_repository = providers.Factory(SessionSectionRepository, session_factory=database.provided.session)
    section_instruction_repository = providers.Factory(SectionInstructionRepository, session_factory=database.provided.session)
    section_iteration_repository = providers.Factory(SectionIterationRepository, session_factory=database.provided.session)
    section_draft_repository = providers.Factory(SectionDraftRepository, session_factory=database.provided.session)
    global_instruction_repository = providers.Factory(GlobalInstructionRepository, session_factory=database.provided.session)
    prompt_execution_repository = providers.Factory(PromptExecutionRepository, session_factory=database.provided.session)
    model_output_repository = providers.Factory(ModelOutputRepository, session_factory=database.provided.session)

    chat_session_service = providers.Factory(
        ChatSessionService,
        chat_session_repository=chat_session_repository,
        session_section_repository=session_section_repository,
        template_service=template_service,
        document_type_service=document_type_service,
        prompt_version_service=prompt_version_service,
    )
    session_section_service = providers.Factory(
        SessionSectionService,
        session_section_repository=session_section_repository,
        chat_session_repository=chat_session_repository,
        global_instruction_repository=global_instruction_repository,
    )
    prompt_composer = providers.Singleton(PromptComposer)
    section_iteration_service = providers.Factory(
        SectionIterationService,
        section_iteration_repository=section_iteration_repository,
        session_section_repository=session_section_repository,
        chat_session_repository=chat_session_repository,
        global_instruction_repository=global_instruction_repository,
        section_instruction_repository=section_instruction_repository,
        prompt_execution_repository=prompt_execution_repository,
        model_output_repository=model_output_repository,
        prompt_version_service=prompt_version_service,
        llm_service=llm_service,
        model_pricing_service=model_pricing_service,
        retrieval_service=retrieval_service,
        prompt_composer=prompt_composer,
    )
    section_draft_service = providers.Factory(
        SectionDraftService,
        section_draft_repository=section_draft_repository,
        section_iteration_repository=section_iteration_repository,
        section_iteration_service=section_iteration_service,
    )

    output_feedback_repository = providers.Factory(OutputFeedbackRepository, session_factory=database.provided.session)
    output_feedback_service = providers.Factory(
        OutputFeedbackService,
        output_feedback_repository=output_feedback_repository,
        section_iteration_service=section_iteration_service,
    )

    analytics_repository = providers.Factory(AnalyticsRepository, session_factory=database.provided.session)
    analytics_service = providers.Factory(
        AnalyticsService,
        analytics_repository=analytics_repository,
        prompt_version_service=prompt_version_service,
    )
    pdf_engine = providers.Singleton(Xhtml2PdfEngine)
    document_type_report_renderer = providers.Singleton(DocumentTypeReportHtmlRenderer)
    document_type_report_service = providers.Factory(
        DocumentTypeReportService,
        analytics_service=analytics_service,
        renderer=document_type_report_renderer,
        pdf_engine=pdf_engine,
    )
    document_report_renderer = providers.Singleton(DocumentReportHtmlRenderer)
    document_report_service = providers.Factory(
        DocumentReportService,
        session_section_service=session_section_service,
        section_iteration_service=section_iteration_service,
        renderer=document_report_renderer,
        pdf_engine=pdf_engine,
    )
