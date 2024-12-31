import datetime

from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    generator: str = Field(default="Default")


class Model(BaseModel):
    doc_type_id: str
    version: str
    generator: str = Field(default="Default")
    status: str = Field(default="Training")
    is_active: bool = Field(default=False)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    draft_ids: list[str] = Field(default_factory=list)
    trained_model_file_id: str | None = None
    id: str | None = None
