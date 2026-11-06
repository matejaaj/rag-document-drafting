from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.core.container import Container
from app.core.security import get_current_user, CurrentUser
from app.schema.feedback.output_feedback_schema import (
    CreateOutputFeedback,
    OutputFeedbackOut,
    OutputFeedbackPage,
    OutputFeedbackItemOut,
)
from app.services.feedback.output_feedback_service import OutputFeedbackService

router = APIRouter(prefix="/output-feedback", tags=["output-feedback"])


@router.post("", response_model=OutputFeedbackOut)
@inject
def create_output_feedback(
    payload: CreateOutputFeedback,
    user: CurrentUser = Depends(get_current_user),
    output_feedback_service: OutputFeedbackService = Depends(Provide[Container.output_feedback_service]),
):

    return output_feedback_service.add(payload, user_id=user.id, user_email=user.email)


@router.get("/by-prompt/{prompt_id}", response_model=OutputFeedbackPage)
@inject
def list_feedback_for_prompt(
    prompt_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    output_feedback_service: OutputFeedbackService = Depends(Provide[Container.output_feedback_service]),
):
    return output_feedback_service.list_for_prompt(prompt_id, page=page, per_page=per_page)


@router.get("/by-version/{version_id}", response_model=OutputFeedbackPage)
@inject
def list_feedback_for_version(
    version_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    output_feedback_service: OutputFeedbackService = Depends(Provide[Container.output_feedback_service]),
):
    return output_feedback_service.list_for_version(version_id, page=page, per_page=per_page)


@router.get("/{feedback_id}", response_model=OutputFeedbackItemOut)
@inject
def get_output_feedback(
    feedback_id: int,
    output_feedback_service: OutputFeedbackService = Depends(Provide[Container.output_feedback_service]),
):
    return output_feedback_service.get(feedback_id)
