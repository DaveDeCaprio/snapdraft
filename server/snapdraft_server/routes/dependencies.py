from pathlib import Path
from typing import Generator

from fastapi import BackgroundTasks

from snapdraft_server.core.default_doc_generator import DefaultDocGenerator
from snapdraft_server.services.doc_type_service import DocumentTypeService
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.services.draft_service import DraftService
from snapdraft_server.services.file_service import FileService
from snapdraft_server.services.model_service import ModelService


def get_local_cache_dir() -> Path:
    raise AssertionError("Should be overridden in the app dependencies.")


def get_dspy_dir() -> Path:
    raise AssertionError("Should be overridden in the app dependencies.")


def get_mongo_client() -> Generator[SnapdraftMongo, any, None]:
    raise AssertionError("get_db should be overridden in the app dependencies.")


def get_doc_type_service() -> DocumentTypeService:
    raise AssertionError("should be overridden in the app dependencies.")


def get_file_service() -> FileService:
    raise AssertionError("should be overridden in the app dependencies.")


def get_draft_service(background_tasks: BackgroundTasks) -> DraftService:
    raise AssertionError("should be overridden in the app dependencies.")


def get_model_service(background_tasks: BackgroundTasks) -> ModelService:
    raise AssertionError("should be overridden in the app dependencies.")


def get_generator_name():
    return "DefaultGenerator"


def get_generator(name: str):
    assert name == "DefaultGenerator"
    return DefaultDocGenerator()
