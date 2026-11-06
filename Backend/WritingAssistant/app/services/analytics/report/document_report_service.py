from __future__ import annotations
from typing import List, Optional, Tuple

from app.services.chat.session_section_service import SessionSectionService
from app.services.chat.section_iteration_service import SectionIterationService
from app.services.analytics.report.document_report_renderer import DocumentReportHtmlRenderer
from app.services.analytics.report.report_models import DocumentReportSelection, PdfEngine


class DocumentReportService:

    INCLUDE_EMPTY_SECTIONS = False

    def __init__(
        self,
        session_section_service: SessionSectionService,
        section_iteration_service: SectionIterationService,
        renderer: DocumentReportHtmlRenderer,
        pdf_engine: PdfEngine,
    ):
        self.session_section_service = session_section_service
        self.section_iteration_service = section_iteration_service
        self.renderer = renderer
        self.pdf_engine = pdf_engine

    @staticmethod
    def _iteration_text(iteration) -> str:
        if not iteration:
            return ""
        if iteration.section_draft and iteration.section_draft.content:
            return iteration.section_draft.content
        return (iteration.model_output.generated_text if iteration.model_output else None) or ""

    def build_pdf(
        self,
        session_id: int,
        user_id: int,
        title_override: Optional[str],
        selections: List[DocumentReportSelection],
    ) -> bytes:
        overview = self.session_section_service.get_session_overview(session_id, user_id)
        selected_seq_no_by_section_id = {
            selection.section_id: selection.seq_no for selection in selections if selection.seq_no is not None
        }

        report_sections: List[Tuple[str, str]] = []
        for section in sorted(overview.sections, key=lambda section: (section.position or 0, section.id)):
            selected_seq_no = selected_seq_no_by_section_id.get(section.id)
            iteration = (
                self.section_iteration_service.find_by_seq_no(section.id, selected_seq_no)
                if selected_seq_no is not None
                else section.latest_iteration
            )
            section_text = self._iteration_text(iteration).strip()
            if section_text or self.INCLUDE_EMPTY_SECTIONS:
                report_sections.append(((section.name or "Sekcija").strip(), section_text))

        title = (title_override or overview.title or "Dokument").strip()
        return self.pdf_engine.html_to_pdf(self.renderer.render(title=title, sections=report_sections))
