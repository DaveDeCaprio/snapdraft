import copy
import logging
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import dspy
import pymupdf4llm
from pydantic import BaseModel, Field

from snapdraft_server.core.doc_generator import DocGenerator, SourceFile, GeneratedDoc
from snapdraft_server.core.doc_section import DocSection
from snapdraft_server.core.doc_template import (
    DocTemplate,
    SourceReference,
    SourceContext,
    SectionInstructions,
)
from snapdraft_server.dspy_helpers.typed_predictor_signature import (
    TypedPredictorSignature,
)

logger = logging.getLogger(__name__)


class SectionSelector(BaseModel):
    class Input(BaseModel):
        section_title: str
        names: list[str]

    class Output(BaseModel):
        selected_name: str

    def select(self, section_title: str, names: list[str]) -> str:
        signature = TypedPredictorSignature.create(
            SectionSelector.Input, SectionSelector.Output
        )
        cot = dspy.ChainOfThought(signature)
        return cot(section_title=section_title, names=names).selected_name


class DefaultDocGenerator(BaseModel):
    section_selector: SectionSelector = Field(default_factory=SectionSelector)

    def get_version(self):
        return "0.0.3"

    def parse_source_file(self, source_file: SourceFile) -> DocSection:
        extension = Path(source_file.original_filename).suffix
        match extension:
            case ".docx":
                markdown = self._pandoc_convert_to_markdown(
                    source_file.path, extension[1:]
                )
            case ".pdf":
                markdown = pymupdf4llm.to_markdown(source_file.path)
            case _:
                raise ValueError(f"File type `{extension}` is currently unsupported")
        return DocSection.parse_markdown(source_file.name, markdown)

    def generate(
        self,
        doc_template: DocTemplate,
        source_files: dict[str, DocSection],
        previous_version: str | None = None,
        user_prompt: str | None = None,
    ):
        """Main method for the doc generator.  Generates an entirely new file from the source
        docs."""
        new_doc = copy.deepcopy(doc_template.parsed_doc)
        for si in doc_template.section_instructions:
            section_text = self._generate_section(
                si, source_files, previous_version, user_prompt
            )
            section = new_doc.find_section_by_id(si.section_id)
            section.intro_text = section_text
        new_markdown = new_doc.as_markdown()
        logger.info(f"Generated:\n{new_markdown}")
        return GeneratedDoc(markdown=new_markdown, explanation_of_changes="")

    def _generate_section(
        self,
        section_instructions: SectionInstructions,
        source_files: dict[str, BaseModel],
        previous_version: str | None,
        user_prompt: str | None,
    ):
        """Generates a new version of this document section.
        Can do de novo generation using just the source files, or can do updates by taking in a
        user_prompt and/or a previous version."""
        # assert (
        #     previous_version is None and user_prompt is None
        # ), "Need to implement updates."
        context = self._create_context(
            section_instructions.source_sections, source_files
        )
        result = section_instructions.authorer.generate(context)
        return result + "\n"

    def _create_context(
        self,
        source_sections: list[SourceReference],
        source_files: dict[str, DocSection],
    ) -> list[SourceContext]:
        """Pulls the relevant sections from the source files to create the context string."""
        ret = []
        for reference in source_sections:
            source_file = source_files[reference.doc_name]
            if reference.section_name is None:
                source_section = source_file
            else:
                source_section = self._find_source_section(
                    source_file, reference.section_name
                )
            markdown = source_section.as_markdown()
            ret.append(
                SourceContext(
                    source_file_name=reference.doc_name,
                    section_title=reference.section_name,
                    markdown=markdown,
                )
            )
        return ret

    def _find_source_section(self, source_file: DocSection, section_title: str):
        """Finds the section of the source document that best corresponds with the section title."""
        names = source_file.get_section_names()
        selected_section = self.section_selector.select(
            section_title=section_title, names=names
        )
        logger.debug(
            f"Selected section {selected_section} for {section_title} from {names}"
        )
        ret = source_file.find_section_by_name(selected_section)
        return ret

    @staticmethod
    def _pandoc_convert_to_markdown(input_file: Path, file_type: str):
        """
        Converts a DOCX file to Markdown format using Pandoc.
        """
        with NamedTemporaryFile() as output_file:
            command = [
                "pandoc",
                "-f",
                file_type,
                "-t",
                "markdown",
                "--atx-headers",
                input_file,
                "-o",
                output_file.name,
            ]
            subprocess.run(command, check=True)
            with open(output_file.name, "rt") as f:
                markdown = f.read()
                return markdown
