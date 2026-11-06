from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routes import api_v1_router
from app.core.container import Container
from app.core.initial_data import add_initial_data
from app.core.security import get_current_user

from app.core.vector_client import (
    is_ready as is_vector_store_ready,
    close as close_vector_store_client,
    get_client as get_vector_store_client,
)
from app.core.vector_schema import ensure_minimal_collections


def _openapi_with_gateway_headers(app: FastAPI) -> dict:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=getattr(app, "description", None),
    )
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["XUserId"] = {"type": "apiKey", "name": "x-user-id", "in": "header"}
    security_schemes["XUserRole"] = {"type": "apiKey", "name": "x-user-role", "in": "header"}
    security_schemes["XUserEmail"] = {"type": "apiKey", "name": "x-email", "in": "header"}

    openapi_schema["security"] = [{"XUserId": [], "XUserRole": [], "XUserEmail": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = container.database()
    database.create_tables()
    add_initial_data(database)

    if not is_vector_store_ready():
        raise RuntimeError(
            "Weaviate is not ready (check docker-compose, the 8081:8080 port mapping and the network)."
        )
    ensure_minimal_collections()
    yield
    close_vector_store_client()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="writing-assistant-api",
        openapi_url="/api/openapi.json",
        version="0.0.1",
        dependencies=[Depends(get_current_user)],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200", "http://localhost:9000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/writing-assistant/health")
    def health_check():
        return "service is working"

    @app.get("/writing-assistant/vector/health")
    def vector_store_health():
        return {"weaviate_ready": is_vector_store_ready()}

    @app.get("/writing-assistant/vector/collections")
    def vector_store_collections():
        return {"collections": list(get_vector_store_client().collections.list_all())}

    app.include_router(api_v1_router, prefix="/writing-assistant")
    app.openapi = lambda: _openapi_with_gateway_headers(app)
    return app


container = Container()
app = create_app()
