from __future__ import annotations

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from snapdraft_server.core.doc_section import DocSection
from snapdraft_server.core.doc_template import (
    DocTemplate,
)


class SourceFile(BaseModel):
    name: str
    original_filename: str
    path: Path


class GeneratedDoc(BaseModel):
    markdown: str
    explanation_of_changes: str


class DocGenerator(Protocol):
    """An interface for document generators."""

    def get_version(self) -> str:
        """Identifies the version of the preprocessor, used for caching.

        SnapDraft saves preprocessed versions of the source files to save time on subsequence calls.
        If the version number changes, SnapDraft will rerun the preprocessor.
        """
        ...

    def parse_source_file(self, source_file: SourceFile) -> DocSection:
        """Parse the source files.

        Returns a dictionary of the source file names to a Pydantic object representing their
        contents.
        """
        ...

    def generate(
        self,
        doc_template: DocTemplate,
        source_files: dict[str, DocSection],
        previous_version: str | None = None,
        user_prompt: str | None = None,
    ) -> GeneratedDoc:
        """Generates a new document"""
        ...
