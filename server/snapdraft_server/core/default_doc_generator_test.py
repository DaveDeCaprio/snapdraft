import os

import dspy

from snapdraft_server.core.default_doc_generator import DefaultDocGenerator
from snapdraft_server.core.doc_generator import DocGenerator
from snapdraft_server.core.doc_section import DocSection
from snapdraft_server.core.doc_template import DocTemplate, SectionInstructions


def get_basedir() -> str:
    """Finds the base directory containing 'snapdraft_server'.

    Starts at the current directory and traverses upward until it finds
    a directory with 'snapdraft_server' as a subdirectory.

    Returns:
        str: The path to the base directory.

    Raises:
        FileNotFoundError: If no such directory is found.
    """
    current_dir = os.getcwd()

    while True:
        if os.path.isdir(os.path.join(current_dir, "snapdraft_server")):
            return current_dir

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            raise FileNotFoundError("No directory containing 'snapdraft_server' found.")

        current_dir = parent_dir


def result_file(path: str):
    full_path = f"{get_basedir()}/{path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path


def example_file(path: str):
    return f"{get_basedir()}/{path}"


def test_doc_preprocessor():
    in_file = example_file(
        "../apps2/projects/CSR/data/inputs/GCT3013-01/GCT3013-01-ClinicalStudyReport-Escalation-Mod.docx"
    )
    out_file = result_file("target/test/processors/example.Md")
    markdown = DefaultDocGenerator._pandoc_convert_to_markdown(in_file, "docx")
    with open(out_file, "wt") as f:
        f.write(markdown)


def test_default_doc_generator():
    llm = dspy.LM(model="gpt-4o", max_tokens=4096)
    dspy.settings.configure(lm=llm)

    generator = DocGenerator()
    template = DocTemplate(
        title="Movie Meta-Review",
        template_md="""
An autogenerated movie review

# Title

# Comments

## Average Rating

""",
        section_instructions=[
            SectionInstructions(section_id=[0], source_sections=[("Review1", None)]),
            SectionInstructions(
                section_id=[1, 0], source_sections=[("Review2", "Rating")]
            ),
        ],
    )
    source_files = {
        "Review1": DocSection.parse_markdown(
            "Review1", "The movie was 'Life is Beautiful'"
        ),
        "Review2": DocSection.parse_markdown(
            "Review2",
            """
# Review
# Rating
It was a 5
""",
        ),
    }

    result = generator.generate(template, source_files)
    generated = result.as_markdown()
    assert "An autogenerated movie review" in generated
    assert "## Average Rating" in generated
