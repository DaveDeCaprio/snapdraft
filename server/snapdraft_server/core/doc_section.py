from __future__ import annotations

import logging
import re

from pydantic import BaseModel, model_validator, field_validator

logger = logging.getLogger(__name__)


class DocSection(BaseModel):
    title: str
    """The header for this section (or the title of the document for the root section)"""
    intro_text: str
    """The text that appears before the first section identifier"""
    subsections: list[DocSection]
    """A list of child sections."""

    @field_validator("subsections", mode="after")
    @classmethod
    def validate_unique_subsection_titles(cls, subsections):
        """Ensure subsection titles are unique."""
        titles = [section.title for section in subsections]
        if len(titles) != len(set(titles)):
            raise ValueError(f"Subsections of didn't have unique titles. {titles}")
        return subsections

    def get_section_names(self):
        """Returns the names of the sections in this document.  Each name is fully qualified, it
        returns the names of all the parent sections, separated by backslashes.  Does not include
        the document title in the section names."""
        return [n for ss in self.subsections for n in ss._recurse_names("")]

    def get_section_ids(self):
        """Returns the section ids for the sections in this document."""
        return self._recurse_ids([])

    def find_section_by_id(self, section_id: list[int]):
        if section_id:
            return self.subsections[section_id[0]].find_section_by_id(section_id[1:])
        else:
            return self

    def find_section_by_name(self, name: str):
        """Finds a section using a backslash separated version of the name."""
        return self._find_section_by_name_parts(name.split("\\"))

    def _find_section_by_name_parts(self, name_parts: list[str]):
        """Finds a section going down through the names at each level."""
        if name_parts:
            for s in self.subsections:
                if s.title == name_parts[0]:
                    return s._find_section_by_name_parts(name_parts[1:])
        else:
            return self

    def _recurse_names(self, current_path: str):
        """Returns the names of the sections in this document.  Each name is fully qualified, it
        returns the names of all the parent sections, separated by backslashes."""
        self_path = current_path + self.title
        recurse_path = self_path + "/"
        return [
            self_path,
            *(n for ss in self.subsections for n in ss._recurse_names(recurse_path)),
        ]

    def _recurse_ids(self, current_list: list[int]) -> list[list[int]]:
        """Returns the names of the sections in this document.  Each name is fully qualified, it
        returns the names of all the parent sections, separated by backslashes."""
        logger.info(f"{self.title}, {current_list}")
        return [
            current_list,
            *(
                n
                for ix, ss in enumerate(self.subsections)
                for n in ss._recurse_ids([*current_list, ix])
            ),
        ]

    def as_markdown(self, level=0) -> str:
        """Returns this section (and subsections) formatted as a markdown string."""
        if level == 0 or not self.title:
            title = ""
        else:
            title = f"{'#'*level} {self.title}\n"
        subsections = "".join(_.as_markdown(level + 1) for _ in self.subsections)
        return f"{title}{self.intro_text}{subsections}"

    @staticmethod
    def parse_markdown(title: str, md: str) -> "DocSection":
        # Split the markdown into lines
        lines = md.splitlines()
        sections = []

        # Track the current level of subsections
        current_section = DocSection(title=title, intro_text="", subsections=[])
        section_stack = [current_section]

        # Define a regex for identifying headers
        header_regex = re.compile(r"^(\d+\.\s*)?(#{1,6})\s+(.*?)\s*$")

        for line in lines:
            match = header_regex.match(line)
            if match:
                header_level = len(match.group(2))
                section_number = (match.group(1) + " ") if match.group(1) else ""
                header_title = section_number + match.group(3)

                # The section stack has the root at the bottom
                while len(section_stack) > header_level:
                    section_stack.pop()

                while len(section_stack) < header_level:
                    skipped_section = DocSection(
                        title="", intro_text="", subsections=[]
                    )
                    section_stack[-1].subsections.append(skipped_section)
                    section_stack.append(skipped_section)

                new_section = DocSection(
                    title=header_title, intro_text="", subsections=[]
                )
                section_stack[-1].subsections.append(new_section)
                section_stack.append(new_section)
            else:
                # Non-header line, add to the intro_text of the current section
                if section_stack:
                    section_stack[-1].intro_text += line + "\n"

        return current_section
