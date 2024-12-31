import dspy
from dotenv import load_dotenv
from pydantic import BaseModel

from snapdraft_server.dspy_helpers.typed_predictor_signature import TypedPredictorSignature

class SectionLookupInput(BaseModel):
    section_title: str
    names: list[str]

class SectionLookupOutput(BaseModel):
    selected_name: str

signature = TypedPredictorSignature.create(SectionLookupInput, SectionLookupOutput)
print(type(signature))

cot = dspy.ChainOfThought(signature)

load_dotenv()
llm = dspy.LM(model="gpt-4o", max_tokens=4096)
dspy.settings.configure(lm=llm)

input = SectionLookupInput(section_title = "History", names = ["Introduction", "Early History",
                                                               "Later Years"]
)

ret = cot(**input.model_dump())
print(ret.selected_name)

# target_section_number: str
# target_title: str
# sources: Optional[list[DocSectionWithDocName]] = None
