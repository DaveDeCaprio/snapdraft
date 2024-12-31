import logging

import pytest

from snapdraft_server.core.doc_section import DocSection

logger = logging.getLogger(__name__)


@pytest.fixture
def example_doc_section():
    return DocSection(
        title="Doc Title",
        intro_text="\nPretext\n\n",
        subsections=[
            DocSection(title="Intro", intro_text="\nIntro paragraph\n", subsections=[]),
            DocSection(
                title="Second Section",
                intro_text="",
                subsections=[
                    DocSection(
                        title="First subsection",
                        intro_text="some text\n",
                        subsections=[
                            DocSection(
                                title="First subsubsection",
                                intro_text="",
                                subsections=[],
                            )
                        ],
                    )
                ],
            ),
            DocSection(
                title="Third Section",
                intro_text="",
                subsections=[
                    DocSection(
                        title="",
                        intro_text="",
                        subsections=[
                            DocSection(
                                title="Skipped level",
                                intro_text="Text\n",
                                subsections=[],
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def test_doc_section_empty():
    md = ""
    doc_root = DocSection.parse_markdown("Doc Title", md)
    assert doc_root == DocSection(
        title="Doc Title",
        intro_text="",
        subsections=[],
    )


def test_doc_section_markdown(example_doc_section):
    md = """
Pretext

# Intro

Intro paragraph
# Second Section
## First subsection
some text
### First subsubsection
# Third Section
### Skipped level
Text
"""
    doc_root = DocSection.parse_markdown("Doc Title", md)
    assert doc_root == example_doc_section


def test_find_section_finds_root(example_doc_section):
    assert example_doc_section.find_section_by_id([]) == example_doc_section


def test_find_section_finds_nested(example_doc_section):
    assert (
        example_doc_section.find_section_by_id([1, 0, 0]).title == "First subsubsection"
    )


def test_get_names(example_doc_section):
    names = example_doc_section.get_section_names()

    assert names == [
        "Intro",
        "Second Section",
        "Second Section\\First subsection",
        "Second Section\\First subsection\\First subsubsection",
        "Third Section",
        "Third Section\\",
        "Third Section\\\\Skipped level",
    ]


def test_get_names(example_doc_section):
    names = example_doc_section.get_section_names()

    assert names == [
        "Intro",
        "Second Section",
        "Second Section\\First subsection",
        "Second Section\\First subsection\\First subsubsection",
        "Third Section",
        "Third Section\\",
        "Third Section\\\\Skipped level",
    ]


def test_find_section_by_name(example_doc_section):
    assert example_doc_section.find_section_by_name(
        "Second Section\\First subsection"
    ) == example_doc_section.find_section_by_id([1, 0])


def test_as_markdown():
    md = """
Pretext

# Intro

Intro paragraph
# Second Section
## First subsection
some text
### First subsubsection
# Third Section
### Skipped level
Text
"""
    reconstructed = DocSection.parse_markdown("title", md).as_markdown()
    assert reconstructed == md


def test_parse_section_number_first():
    markdown = """
Intro text

5.  # Section with number first

1.  ## Subsection with number first

content

## Subsection with no number    
"""
    reconstructed = DocSection.parse_markdown("title", markdown)
    logger.info(f"{reconstructed}")
    assert reconstructed.subsections[0].title == "5.   Section with number first"
    assert reconstructed.get_section_names() == [
        "5.   Section with number first",
        "5.   Section with number first/1.   Subsection with number first",
        "5.   Section with number first/Subsection with no number",
    ]


def test_get_section_ids(example_doc_section):
    assert example_doc_section.get_section_ids() == [
        [],
        [0],
        [1],
        [1, 0],
        [1, 0, 0],
        [2],
        [2, 0],
        [2, 0, 0],
    ]


def test_parse_2():
    markdown = """
> **Report**
>
> **Doc Number: 23947829**

**Bold text**

> **Centered Bold**

intro
# TITLE PAGE

+----------------------------------+----------------------------------+
| > **Title table**                | > First section                  |
+==================================+==================================+
| > **Header**                     | > Details                        |
+----------------------------------+----------------------------------+
| > **Authors**                    | > Decapr                         |
+----------------------------------+----------------------------------+

# SUMMARY

+----------------------------------+----------------------------------+
| > **Authors**                    | > Decapr                         |
+==================================+==================================+
| > **Date**                       | > 12/31/204                      |
+----------------------------------+----------------------------------+
    """
    names = DocSection.parse_markdown("title", markdown).get_section_names()
    logger.info(names)
    assert names == ["TITLE PAGE", "SUMMARY"]
