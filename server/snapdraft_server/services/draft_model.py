from pydantic import BaseModel, Field


class DraftBase(BaseModel):
    name: str
    use_for_training: bool = False
    output_file_id: str | None = None

    source_file_ids: dict[str, str] = Field(default_factory=dict)
    """A dictionary of source names to file ids"""

    class Config:
        populate_by_name = True


class DraftCreate(DraftBase):
    pass


class Draft(DraftBase):
    doc_type_id: str
    id: str | None = None
    output_file_md_id: str | None = None
    """A version of the output file converted to markdown.  If the output is already markdown, 
    this will be the same as output_file_id"""


class GenerateDraftResult(BaseModel):
    text: str


class RegeneratedDraftResult(BaseModel):
    text: str
    message: str
