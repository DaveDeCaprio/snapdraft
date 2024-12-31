import dspy
import pytest
from pydantic import ValidationError

from snapdraft_server.core.doc_template import DocTemplate, SectionInstructions


def test_doc_template_validator():
    markdown = """# Header"""
    with pytest.raises(ValidationError):
        DocTemplate(title="test", template_md=markdown, section_instructions=[SectionInstructions(
            section_id=[4,1], generator = dspy.ChainOfThought("patient_profile -> final_narrative"),
            source_sections=[]
        )])