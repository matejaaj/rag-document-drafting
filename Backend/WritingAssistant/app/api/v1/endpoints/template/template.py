from typing import Optional
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.container import Container
from app.core.security import get_current_user_id
from app.schema.template.template_schema import TemplatePageOut, TemplateOut
from app.services.template.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=TemplatePageOut)
@inject
def list_templates(
    page: int = 1,
    per_page: int = 20,
    _: int = Depends(get_current_user_id),
    search_term: Optional[str] = None,
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    return template_service.list(page=page, per_page=per_page, search_term=search_term)


@router.post("", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
@inject
async def create_template(
    name: str = Form(...),
    document_type_id: int = Form(...),
    file: UploadFile = File(...),
    repo_folder_id: Optional[int] = Form(None),
    user_id: int = Depends(get_current_user_id),
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    content = await file.read()
    return template_service.add_from_upload(
        name=name.strip(),
        document_type_id=document_type_id,
        filename=file.filename or "",
        content=content,
        mime_type=file.content_type or "application/octet-stream",
        created_by=user_id,
        repo_folder_id=repo_folder_id,
    )


@router.delete("/{template_id}", status_code=204)
@inject
def delete_template(
    template_id: int,
    user_id: int = Depends(get_current_user_id),
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    template_service.remove(template_id, user_id)
    return
