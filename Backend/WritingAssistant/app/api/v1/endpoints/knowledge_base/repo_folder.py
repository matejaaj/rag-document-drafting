from typing import Optional
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.core.container import Container
from app.core.security import get_current_user_id, require_admin, CurrentUser
from app.schema.knowledge_base.repo_folder_schema import (
    RepoFolderOut,
    RepoFolderPageOut,
    CreateRepoFolder,
    PatchRepoFolder,
)
from app.services.knowledge_base.repo_folder_service import RepoFolderService

router = APIRouter(prefix="/repo-folders", tags=["repo-folders"])


@router.get("", response_model=RepoFolderPageOut)
@inject
def list_repo_folders(
    page: int = 1,
    per_page: int = 20,
    parent_id: Optional[int] = None,
    repo_folder_service: RepoFolderService = Depends(Provide[Container.repo_folder_service]),
    _: CurrentUser = Depends(require_admin),
):
    return repo_folder_service.list(page=page, per_page=per_page, parent_id=parent_id)


@router.get("/{folder_id}", response_model=RepoFolderOut)
@inject
def get_repo_folder(
    folder_id: int,
    repo_folder_service: RepoFolderService = Depends(Provide[Container.repo_folder_service]),
    _: CurrentUser = Depends(require_admin),
):
    return repo_folder_service.get(folder_id)


@router.post("", response_model=RepoFolderOut, status_code=status.HTTP_201_CREATED)
@inject
def create_repo_folder(
    payload: CreateRepoFolder,
    user_id: int = Depends(get_current_user_id),
    repo_folder_service: RepoFolderService = Depends(Provide[Container.repo_folder_service]),
    _: CurrentUser = Depends(require_admin),
):
    return repo_folder_service.add(payload, user_id)


@router.patch("/{folder_id}", response_model=RepoFolderOut)
@inject
def update_repo_folder(
    folder_id: int,
    payload: PatchRepoFolder,
    repo_folder_service: RepoFolderService = Depends(Provide[Container.repo_folder_service]),
    _: CurrentUser = Depends(require_admin),
):
    return repo_folder_service.update(folder_id, payload)


@router.delete("/{folder_id}", status_code=204)
@inject
def delete_repo_folder(
    folder_id: int,
    repo_folder_service: RepoFolderService = Depends(Provide[Container.repo_folder_service]),
    _: CurrentUser = Depends(require_admin),
):
    repo_folder_service.remove(folder_id)
    return
