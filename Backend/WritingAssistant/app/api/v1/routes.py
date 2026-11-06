from fastapi import APIRouter

from app.api.v1.endpoints.chat.chat_session import router as chat_session_router
from app.api.v1.endpoints.chat.session_section import router as session_section_router
from app.api.v1.endpoints.prompt.prompt import router as prompt_router
from app.api.v1.endpoints.prompt.prompt_version import router as prompt_version_router
from app.api.v1.endpoints.template.template import router as template_router
from app.api.v1.endpoints.document_type.document_type import router as document_type_router
from app.api.v1.endpoints.feedback.output_feedback import router as output_feedback_router
from app.api.v1.endpoints.analytics.analytics import router as analytics_router
from app.api.v1.endpoints.analytics.report import router as report_router
from app.api.v1.endpoints.knowledge_base.storage_object import router as storage_object_router
from app.api.v1.endpoints.knowledge_base.repo_folder import router as repo_folder_router


api_v1_router = APIRouter()
feature_routers = [
    chat_session_router,
    session_section_router,
    prompt_router,
    prompt_version_router,
    template_router,
    document_type_router,
    output_feedback_router,
    analytics_router,
    report_router,
    storage_object_router,
    repo_folder_router,
]

for feature_router in feature_routers:
    feature_router.tags = ["v1"]
    api_v1_router.include_router(feature_router)
