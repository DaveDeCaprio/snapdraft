import logging

from fastapi import APIRouter, Depends, UploadFile, File
from starlette.responses import StreamingResponse

from snapdraft_server.routes.dependencies import get_file_service
from snapdraft_server.services.file_model import StoredFileMetadata, StoredFile
from snapdraft_server.services.file_service import FileService

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/upload/", response_model=StoredFile, operation_id="upload_file")
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
):
    metadata = StoredFileMetadata.from_upload_file(file)
    return await file_service.upload_from_stream(file.file, metadata)


@router.get(
    "/{file_id}",
    response_model=StoredFile,
    operation_id="read_stored_file",
)
async def read_stored_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
):
    return await file_service.get(file_id)


@router.get(
    "/{file_id}/contents",
    operation_id="read_contents",
)
async def read_contents(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
):
    return await file_service.get_streaming_response(file_id)
