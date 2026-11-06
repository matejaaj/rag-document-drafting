from __future__ import annotations
from typing import Any, Dict, List

from app.services.analytics.analytics_service import AnalyticsService
from app.services.analytics.report.document_type_report_renderer import DocumentTypeReportHtmlRenderer
from app.services.analytics.report.report_models import DOCUMENT_TYPE_REPORT_COLUMNS, DocumentTypeReportParams, PdfEngine


class DocumentTypeReportService:

    def __init__(
        self,
        analytics_service: AnalyticsService,
        renderer: DocumentTypeReportHtmlRenderer,
        pdf_engine: PdfEngine,
    ):
        self.analytics_service = analytics_service
        self.renderer = renderer
        self.pdf_engine = pdf_engine

    def build_pdf(self, params: DocumentTypeReportParams) -> bytes:
        rows = self.analytics_service.get_document_type_report(
            params.from_ts, params.to_ts, params.document_type_id, params.include_total
        ) or []

        document_type_rows, total_row = self._split_total(rows)
        sorted_rows = self._sort_rows(document_type_rows, params.sort_key, params.sort_direction)
        report_rows = [*sorted_rows, *([total_row] if total_row else [])]

        html = self.renderer.render(report_rows, params)
        return self.pdf_engine.html_to_pdf(html)

    def _split_total(self, rows: List[Dict[str, Any]]):
        """The total row has no document_type_id."""
        total_row = None
        document_type_rows = []
        for row in rows:
            if row.get("document_type_id") is None:
                total_row = row
            else:
                document_type_rows.append(row)
        return document_type_rows, total_row

    def _sort_rows(self, rows: List[Dict[str, Any]], sort_key: str, sort_direction: str) -> List[Dict[str, Any]]:
        valid_keys = {key for key, _ in DOCUMENT_TYPE_REPORT_COLUMNS}
        if sort_key not in valid_keys:
            sort_key = "document_type_name"
        descending = sort_direction.lower() == "desc"

        def sort_value(row):
            value = row.get(sort_key)
            if value is None:
                return (1, "")
            return (0, value) if isinstance(value, str) else (0, float(value))
        return sorted(rows, key=sort_value, reverse=descending)
