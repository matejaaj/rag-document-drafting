from typing import Optional
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from app.core.container import Container
from app.core.security import require_admin, CurrentUser
from app.schema.analytics.analytics_schema import AnalyticsOut
from app.services.analytics.analytics_service import AnalyticsService
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/prompt-versions/{id}", response_model=AnalyticsOut)
@inject
def get_version_analytics(
    id: int,
    bayes_prior_weight: int = Query(10, description="Bayes prior weight"),
    _: CurrentUser = Depends(require_admin),
    analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
):
    return analytics_service.get_version_analytics(id, bayes_prior_weight=bayes_prior_weight)

@router.get("/prompts/{id}", response_model=AnalyticsOut)
@inject
def get_prompt_analytics(
    id: int,
    bayes_prior_weight: int = Query(10, description="Bayes prior weight"),
    _: CurrentUser = Depends(require_admin),
    analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
):
    return analytics_service.get_prompt_analytics(id, bayes_prior_weight=bayes_prior_weight)


@router.get("/document-type-report")
@inject
def get_document_type_report(
    from_ts: datetime = Query(..., description="ISO 8601 with time zone, e.g. 2025-09-01T00:00:00+02:00"),
    to_ts:   datetime = Query(...),
    document_type_id: Optional[int] = Query(None),
    include_total: bool = Query(True),
    _: CurrentUser = Depends(require_admin),
    analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
):
    return analytics_service.get_document_type_report(from_ts, to_ts, document_type_id, include_total)
