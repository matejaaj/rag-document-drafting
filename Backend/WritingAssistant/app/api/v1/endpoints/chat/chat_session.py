from typing import Optional
from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends
from app.schema.chat.session_overview_schema import SessionOverviewOut

from app.core.container import Container
from app.core.security import get_current_user_id, require_admin, CurrentUser
from app.schema.chat.chat_session_schema import CreateChatSession, ChatSessionOut, CreateTestChatSession, ChatSessionPageOut, PatchChatSessionDocumentType, PatchChatSessionTitle
from app.services.chat.chat_session_service import ChatSessionService
from app.services.chat.session_section_service import SessionSectionService
from dependency_injector.wiring import inject

router = APIRouter(prefix="/chat-sessions", tags=["chat-sessions"])

@router.post("", response_model=ChatSessionOut)
@inject
def create_chat_session(
    payload: CreateChatSession,
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
    user_id: int = Depends(get_current_user_id),
):

    payload.created_by = user_id
    return chat_session_service.add(payload)


@router.get("", response_model=ChatSessionPageOut)
@inject
def list_chat_sessions(
    page: int = 1,
    per_page: int = 20,
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
    search_term: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
):
    return chat_session_service.list(page=page, per_page=per_page, user_id=user_id, search_term=search_term)


@router.get("/{session_id}/overview", response_model=SessionOverviewOut)
@inject
def get_session_overview(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    session_section_service: SessionSectionService = Depends(Provide[Container.session_section_service]),
):
    return session_section_service.get_session_overview(session_id, user_id)


@router.patch("/{chat_session_id}/title", response_model=ChatSessionOut)
@inject
def update_chat_session_title(
    chat_session_id: int,
    payload: PatchChatSessionTitle,
    user_id: int = Depends(get_current_user_id),
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
):
    return chat_session_service.update_title(chat_session_id, payload.title, user_id)

@router.delete("/{chat_session_id}", status_code=204)
@inject
def delete_chat_session(
    chat_session_id: int,
    user_id: int = Depends(get_current_user_id),
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
):
    chat_session_service.remove(chat_session_id, user_id)
    return


@router.patch("/{chat_session_id}/document-type", response_model=ChatSessionOut)
@inject
def update_chat_session_document_type(
    chat_session_id: int,
    payload: PatchChatSessionDocumentType,
    user_id: int = Depends(get_current_user_id),
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
):
    return chat_session_service.update_document_type(chat_session_id, payload.document_type_id, user_id)


@router.post("/test", response_model=ChatSessionOut)
@inject
def create_test_chat_session(
    payload: CreateTestChatSession,
    _: CurrentUser = Depends(require_admin),
    user_id: int = Depends(get_current_user_id),
    chat_session_service: ChatSessionService = Depends(Provide[Container.chat_session_service]),
):
    return chat_session_service.add_test(payload, user_id)
