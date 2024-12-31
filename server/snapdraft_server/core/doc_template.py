from __future__ import annotations

import copy
from functools import cached_property

import dspy
from pydantic import BaseModel, model_validator, field_validator, Field

from snapdraft_server.core.doc_section import DocSection
from snapdraft_server.dspy_helpers.typed_predictor_signature import (
    TypedPredictorSignature,
)


class DocTemplate(BaseModel):
    """Template for generating a document.
    Can include multiple sections in the markdown. The section_instructions contain
    information on how to generate each section that has automated generation.
    If the template_md is empty, the entire document will be generated."""

    title: str
    template_md: str
    section_instructions: list[SectionInstructions]

    @model_validator(mode="after")
    def validate_section_instructions(self):
        """Ensure there is at least one section instruction and that all section
        instructions reference actual sections of the template."""
        if len(self.section_instructions) == 0:
            raise ValueError(
                "Tried to create a DocTemplate with no generation instructions.  At"
                "least one is required or else the document is static (no generation)"
            )
        section_ids = [si.section_id for si in self.section_instructions]
        if len(section_ids) != len(set(tuple(_) for _ in section_ids)):
            raise ValueError(
                f"Template had duplicate SectionInstructions.  Only 1 set of instructions can be created per section.  {section_ids}"
            )
        for id in section_ids:
            try:
                self.parsed_doc.find_section_by_id(id)
            except:
                raise ValueError(
                    f"Template had instructions for section {id}, which isn't a "
                    f"valid section number.  Sections are: {self.parsed_doc.get_section_ids()}"
                )
        return self

    @cached_property
    def parsed_doc(self) -> DocSection:
        return DocSection.parse_markdown(self.title, self.template_md)

    class Config:
        # Exclude the computed property from being serialized to JSON
        json_encoders = {
            property: lambda _: None  # Exclude properties from JSON output
        }


class SourceContext(BaseModel):
    """An extracted section of a source document ot be added to the context."""

    source_file_name: str
    section_title: str | None
    markdown: str


class SectionAuthorer(BaseModel):
    """Does the actual generation of the document section"""

    class Input(BaseModel):
        context: list[SourceContext]

    class Output(BaseModel):
        markdown: str

    def generate(self, context: list[SourceContext]):
        signature = TypedPredictorSignature.create(
            SectionAuthorer.Input, SectionAuthorer.Output
        )
        cot = dspy.ChainOfThought(signature)
        return cot(context=context).markdown


class SourceReference(BaseModel):
    doc_name: str
    section_name: str | None = None


class SectionInstructions(BaseModel):
    section_id: list[int]
    """Identifies which section will be generated.  Indices into the subsections of the 
    DocSection."""
    source_sections: list[SourceReference] = Field(default_factory=list)
    """A list of (Source file name, section name) pairs to include in the context.  If the 
    section name is None, the whole doc is included."""

    authorer: SectionAuthorer = Field(default_factory=SectionAuthorer)
    """A DSPyModule that texts the formatted input context and produces the outputs text."""

    class Config:
        arbitrary_types_allowed = True
