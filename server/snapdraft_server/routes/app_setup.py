import logging
from pathlib import Path

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from snapdraft_server.routes import generator_routes
from snapdraft_server.services.draft_service import DraftService
from snapdraft_server.services.doc_type_service import DocumentTypeService
from snapdraft_server.services.base.snapdraft_mongo import (
    SnapdraftMongo,
)
from snapdraft_server.routes.dependencies import (
    get_dspy_dir,
    get_doc_type_service,
    get_draft_service,
    get_mongo_client,
    get_file_service,
    get_local_cache_dir,
    get_model_service,
)
from snapdraft_server.services.file_service import FileService
from snapdraft_server.services.model_service import ModelService

logger = logging.getLogger(__name__)


def create_app(
    origins: list[str],
    mongo_client: SnapdraftMongo,
    local_cache_dir: Path = None,
    dspy_dir: Path = None,
) -> FastAPI:
    from snapdraft_server.routes import document_type_routes
    from snapdraft_server.routes import file_routes

    app = FastAPI()

    # Add CORS middleware to allow your frontend to access the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def custom_exception_handler(request: Request, exc: Exception):
        # logger.exception(exc)
        request_origin = request.headers.get("Origin")
        allow_origin = request_origin if request_origin in origins else None
        headers = {"Access-Control-Allow-Origin": allow_origin} if allow_origin else {}
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
            headers=headers,
        )

    app.include_router(
        generator_routes.router,
        prefix="/generators",
        tags=["generators"],
    )
    app.include_router(
        document_type_routes.router,
        prefix="/document-types",
        tags=["document-types"],
    )
    app.include_router(
        file_routes.router,
        prefix="/files",
        tags=["files"],
    )

    def override_get_local_cache_dir():
        return local_cache_dir

    if local_cache_dir is not None:
        app.dependency_overrides[get_local_cache_dir] = override_get_local_cache_dir

    def override_get_dspy_dir():
        return dspy_dir

    if dspy_dir is not None:
        app.dependency_overrides[get_dspy_dir] = override_get_dspy_dir

    def override_get_mongo_client():
        return mongo_client

    app.dependency_overrides[get_mongo_client] = override_get_mongo_client

    def override_get_doc_type_service():
        return DocumentTypeService(mongo_client)

    app.dependency_overrides[get_doc_type_service] = override_get_doc_type_service

    def override_get_file_service():
        local_cache_dir = override_get_local_cache_dir()
        return FileService(mongo_client, local_cache_dir)

    app.dependency_overrides[get_file_service] = override_get_file_service

    def override_get_draft_service(background_tasks: BackgroundTasks):
        doc_type_service = override_get_doc_type_service()
        file_service = override_get_file_service()
        return DraftService(
            mongo_client, doc_type_service, file_service, background_tasks
        )

    app.dependency_overrides[get_draft_service] = override_get_draft_service

    def override_get_model_service(background_tasks: BackgroundTasks):
        return ModelService(
            mongo_client,
            doc_type_service=override_get_doc_type_service(),
            file_service=override_get_file_service(),
            draft_service=override_get_draft_service(background_tasks),
            background_tasks=background_tasks,
        )

    app.dependency_overrides[get_model_service] = override_get_model_service

    return app
