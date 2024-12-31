from pydantic import BaseModel, Field


class SourceType(BaseModel):
    name: str
    description: str


class DocumentType(BaseModel):
    name: str
    id: str | None = None
    sources: list[SourceType] = Field(default_factory=list)
    instructions: str | None = None  # Adding instructions field
    template_file_id: str | None = None

    class Config:
        populate_by_name = True
