from snapdraft_server.core.doc_template import (
    DocTemplate,
    SectionInstructions,
    SectionAuthorer,
    SourceReference,
)

template = DocTemplate(
    title="Default Template",
    template_md="""
# Intro

# Section 2
""",
    section_instructions=[
        SectionInstructions(
            section_id=[0],
            source_sections=[SourceReference(doc_name="Files", section_name="Intro")],
            authorer=SectionAuthorer(),
        ),
    ],
)
