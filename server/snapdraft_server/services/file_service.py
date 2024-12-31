import logging
from http.client import HTTPException
from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator

from bson import ObjectId
from starlette.responses import StreamingResponse

from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.services.file_model import StoredFileMetadata, StoredFile

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, client: SnapdraftMongo, local_cache_dir: Path):
        self.client = client
        self.local_cache_dir = local_cache_dir
        self.collection = client.db["fs.files"]

    async def get(self, file_id: str) -> StoredFile:
        metadata = await self._get_metadata(file_id)
        return StoredFile(id=file_id, metadata=metadata)

    async def get_streaming_response(self, file_id: str):
        file = await self.get(file_id)
        return StreamingResponse(
            self.get_download_stream(file_id),
            media_type=file.metadata.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file.metadata.original_filename}"'
            },
        )

    async def upload_text_file(
        self, text: str, metadata: StoredFileMetadata
    ) -> StoredFile:
        stream = BytesIO(text.encode())
        return await self.upload_from_stream(stream, metadata)

    async def upload_from_stream(
        self, stream: any, metadata: StoredFileMetadata
    ) -> StoredFile:
        file_id = await self.client.gridfs.upload_from_stream(
            filename=metadata.original_filename,
            source=stream,
            metadata=metadata.model_dump(),
        )
        return StoredFile(id=str(file_id), metadata=metadata)

    async def get_download_stream(self, file_id: str) -> AsyncGenerator[bytes, None]:
        stream = await self.client.gridfs.open_download_stream(ObjectId(file_id))
        while chunk := await stream.read(1024 * 1024):  # Read in chunks of 1MB
            yield chunk
        stream.close()

    async def get_local_path(self, file_id: str):
        metadata = await self._get_metadata(file_id)
        path = self.local_cache_dir / f"{file_id}.{metadata.extension}"
        if not path.exists():
            with path.open("wb") as f:
                await self.client.gridfs.download_to_stream(ObjectId(file_id), f)
            assert path.exists(), f"Path {path} wasn't created."
        else:
            logger.debug(f"Using existing locally cached file {path}")
        return path

    async def _get_metadata(self, file_id: str) -> StoredFileMetadata:
        file_document = await self.collection.find_one({"_id": ObjectId(file_id)})
        if not file_document:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        metadata = file_document.get("metadata", {})
        return StoredFileMetadata.model_validate(metadata)
