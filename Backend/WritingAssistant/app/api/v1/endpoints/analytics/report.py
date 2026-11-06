from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import Response
from dependency_injector.wiring import Provide, inject
from typing import Optional
from datetime import datetime

from app.core.container import Container
from app.core.security import get_current_user_id, require_admin, CurrentUser

from app.services.analytics.report.document_type_report_service import DocumentTypeReportService
from app.services.analytics.report.document_report_service import DocumentReportService
from app.services.analytics.report.report_models import DocumentTypeReportParams

from app.schema.analytics.report_schema import DocumentReportIn


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _pdf_attachment_response(pdf_bytes: bytes) -> Response:
    filename = f"izvestaj-{datetime.now().strftime('%d-%m-%Y-%H-%M')}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/document-type-report.pdf")
@inject
def get_document_type_report_pdf(
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    document_type_id: Optional[int] = Query(None),
    include_total: bool = Query(True),
    sort_key: str = Query("document_type_name"),
    sort_direction: str = Query("asc"),
    timezone: Optional[str] = Query(None),
    _: CurrentUser = Depends(require_admin),
    document_type_report_service: DocumentTypeReportService = Depends(Provide[Container.document_type_report_service]),
):
    pdf_bytes = document_type_report_service.build_pdf(
        DocumentTypeReportParams(
            from_ts=from_ts,
            to_ts=to_ts,
            document_type_id=document_type_id,
            include_total=include_total,
            sort_key=sort_key,
            sort_direction=sort_direction,
            timezone_name=timezone,
            locale="sr-RS",
        )
    )
    return _pdf_attachment_response(pdf_bytes)


@router.post("/document-report.pdf")
@inject
def get_document_report_pdf(
    session_id: int = Query(..., description="Id of the chat session whose document is rendered"),
    body: DocumentReportIn = Body(...),
    user_id: int = Depends(get_current_user_id),
    document_report_service: DocumentReportService = Depends(Provide[Container.document_report_service]),
):
    pdf_bytes = document_report_service.build_pdf(
        session_id=session_id,
        user_id=user_id,
        title_override=(body.title or "").strip() or None,
        selections=body.selections,
    )
    return _pdf_attachment_response(pdf_bytes)
