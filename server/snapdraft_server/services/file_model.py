import datetime
from pathlib import Path

from fastapi import UploadFile
from pydantic import BaseModel, Field, computed_field


class StoredFileMetadata(BaseModel):
    original_filename: str
    extension: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        populate_by_name = True

    @staticmethod
    def from_upload_file(file: UploadFile):
        extension = Path(file.filename).suffix.lstrip(".")
        return StoredFileMetadata(
            original_filename=file.filename,
            extension=extension,
        )

    @computed_field
    @property
    def content_type(self) -> str:
        match self.extension.lower():
            case "md":
                return "text/markdown"
            case "docx":
                return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            case "pdf":
                return "application/pdf"
            case "txt":
                return "text/plain"
            case "json":
                return "application/json"
            case _:
                return "application/octet-stream"


class StoredFile(BaseModel):
    id: str
    metadata: StoredFileMetadata
