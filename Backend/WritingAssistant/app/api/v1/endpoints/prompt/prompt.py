from typing import Optional
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.security import get_current_user_id, require_admin, CurrentUser
from app.schema.prompt.prompt_schema import CreatePrompt, PromptOut, PromptWithActiveVersionPageOut, PatchPromptTitle


from app.services.prompt.prompt_service import PromptService


router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("", response_model=PromptOut)
@inject
def create_prompt(
    payload: CreatePrompt,
    _: CurrentUser = Depends(require_admin),
    user_id: int = Depends(get_current_user_id),
    prompt_service: PromptService = Depends(Provide[Container.prompt_service]),
):
    return prompt_service.add(payload, user_id)

@router.delete("/{id}", status_code=204)
@inject
def delete_prompt(
    id: int,
    _: CurrentUser = Depends(require_admin),
    prompt_service: PromptService = Depends(Provide[Container.prompt_service]),
):
    prompt_service.remove(id)
    return

@router.get("", response_model=PromptWithActiveVersionPageOut)
@inject
def list_prompts(
    page: int = 1,
    per_page: int = 20,
    search_term: Optional[str] = None,
    prompt_service: PromptService = Depends(Provide[Container.prompt_service]),
    _: CurrentUser = Depends(require_admin),
):
    return prompt_service.list_with_active_versions(page=page, per_page=per_page, search_term=search_term)


@router.patch("/{prompt_id}/title", response_model=PromptOut)
@inject
def update_prompt_title(
    prompt_id: int,
    payload: PatchPromptTitle,
    _: CurrentUser = Depends(require_admin),
    prompt_service: PromptService = Depends(Provide[Container.prompt_service]),
):
    return prompt_service.update_title(prompt_id, payload.title)
