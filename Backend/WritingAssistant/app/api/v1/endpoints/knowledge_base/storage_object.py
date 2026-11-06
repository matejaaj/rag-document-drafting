from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from typing import Optional

from app.core.container import Container
from app.core.security import get_current_user_id, require_admin, CurrentUser
from app.services.knowledge_base.storage_object_service import StorageObjectService
from app.services.rag.vector_service import VectorService
from app.schema.knowledge_base.storage_object_schema import StorageObjectOut, StorageObjectPageOut, PatchStorageObject

router = APIRouter(prefix="/storage-objects", tags=["storage-objects"])


@router.get("", response_model=StorageObjectPageOut)
@inject
def list_storage_objects(
    page: int = 1,
    per_page: int = 20,
    repo_folder_id: Optional[int] = None,
    storage_object_service: StorageObjectService = Depends(Provide[Container.storage_object_service]),
    _: CurrentUser = Depends(require_admin),
):
    return storage_object_service.list(page=page, per_page=per_page, repo_folder_id=repo_folder_id)


@router.get("/{object_id}", response_model=StorageObjectOut)
@inject
def get_storage_object(
    object_id: int,
    storage_object_service: StorageObjectService = Depends(Provide[Container.storage_object_service]),
    _: CurrentUser = Depends(require_admin),
):
    return storage_object_service.get(object_id)


@router.post("", response_model=StorageObjectOut, status_code=status.HTTP_201_CREATED)
@inject
async def create_storage_object(
    file: UploadFile = File(...),
    repo_folder_id: Optional[int] = Form(None),
    user_id: int = Depends(get_current_user_id),
    document_type_id: int = Form(...),
    storage_object_service: StorageObjectService = Depends(Provide[Container.storage_object_service]),
    _: CurrentUser = Depends(require_admin),
):
    content = await file.read()
    return storage_object_service.add_from_upload(
        filename=file.filename or "upload.bin",
        content=content,
        mime_type=file.content_type,
        repo_folder_id=repo_folder_id,
        created_by=user_id,
        document_type_id=document_type_id
    )


@router.patch("/{object_id}", response_model=StorageObjectOut)
@inject
def update_storage_object(
    object_id: int,
    payload: PatchStorageObject,
    storage_object_service: StorageObjectService = Depends(Provide[Container.storage_object_service]),
    _: CurrentUser = Depends(require_admin),
):
    return storage_object_service.update_metadata(object_id, payload)


@router.delete("/{object_id}", status_code=204)
@inject
def delete_storage_object(
    object_id: int,
    storage_object_service: StorageObjectService = Depends(Provide[Container.storage_object_service]),
    _: CurrentUser = Depends(require_admin),
):
    storage_object_service.remove(object_id)
    return


@router.get("/{object_id}/summary")
@inject
def get_storage_object_summary(
    object_id: int,
    vector_service: VectorService = Depends(Provide[Container.vector_service]),
    _: CurrentUser = Depends(require_admin),
):

    return {"summary_text": vector_service.get_summary(object_id)}
