from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.security import get_current_user_id, CurrentUser, get_current_user
from app.schema.chat.session_section_schema import CreateSessionSection, SessionSectionOut, PatchSessionSectionTitle
from app.services.chat.session_section_service import SessionSectionService
from app.services.chat.section_iteration_service import SectionIterationService
from app.services.chat.section_draft_service import SectionDraftService
from app.schema.chat.section_iteration_schema import SectionIterationOut, GenerateIterationIn
from app.schema.chat.section_draft_schema import SaveDraftIn

router = APIRouter(prefix="/session-sections", tags=["session-sections"])


@router.post("", response_model=SessionSectionOut)
@inject
def create_session_section(
    payload: CreateSessionSection,
    session_section_service: SessionSectionService = Depends(Provide[Container.session_section_service]),
):
    return session_section_service.add(payload)


@router.delete("/{id}", status_code=204)
@inject
def delete_session_section(
    id: int,
    user_id: int = Depends(get_current_user_id),
    session_section_service: SessionSectionService = Depends(Provide[Container.session_section_service]),
):
    session_section_service.remove(id, user_id)
    return


@router.get("/{section_id}/iterations/{seq_no}", response_model=SectionIterationOut)
@inject
def get_iteration_by_seq_no(
    section_id: int,
    seq_no: int,
    user_id: int = Depends(get_current_user_id),
    section_iteration_service: SectionIterationService = Depends(Provide[Container.section_iteration_service]),
):
    return section_iteration_service.get_by_seq_no(section_id, seq_no, user_id)


@router.post("/{section_id}/iterations", response_model=SectionIterationOut)
@inject
def generate_iteration(
    section_id: int,
    payload: GenerateIterationIn,
    user: CurrentUser = Depends(get_current_user),
    section_iteration_service: SectionIterationService = Depends(Provide[Container.section_iteration_service]),
):
    return section_iteration_service.generate(section_id, payload, user)


@router.patch("/{session_section_id}/title", response_model=SessionSectionOut)
@inject
def update_session_section_title(
    session_section_id: int,
    payload: PatchSessionSectionTitle,
    user_id: int = Depends(get_current_user_id),
    session_section_service: SessionSectionService = Depends(Provide[Container.session_section_service]),
):
    return session_section_service.update_title(session_section_id, payload.name, user_id)


@router.put("/{section_id}/iterations/{seq_no}/draft", response_model=SectionIterationOut)
@inject
def save_iteration_draft(
    section_id: int,
    seq_no: int,
    payload: SaveDraftIn,
    user_id: int = Depends(get_current_user_id),
    section_draft_service: SectionDraftService = Depends(Provide[Container.section_draft_service]),
):
    return section_draft_service.save_for_iteration(section_id, seq_no, payload.content, user_id)
