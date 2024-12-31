import asyncio
import json
import logging
from io import BytesIO

from fastapi import BackgroundTasks
from pydantic import BaseModel

from snapdraft_server.core.doc_generator import DocGenerator, SourceFile
from snapdraft_server.core.doc_section import DocSection
from snapdraft_server.core.hardcoded_template import template
from snapdraft_server.services.base.base_collection import BaseCollection
from snapdraft_server.services.doc_type_service import DocumentTypeService
from snapdraft_server.services.draft_model import (
    DraftCreate,
    Draft,
    GenerateDraftResult,
    RegeneratedDraftResult,
)
from snapdraft_server.services.base.result_list import ResultList
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.services.file_model import StoredFileMetadata, StoredFile
from snapdraft_server.services.file_service import FileService
from snapdraft_server.util.util import load_model

logger = logging.getLogger(__name__)


class PreprocessedFile(BaseModel):
    """Internal model used to cache preprocessed files."""

    source_file_id: str
    generator_name: str
    generator_version: str
    preprocessed_file_id: str
    id: str | None = None


class DraftService(BaseCollection):
    def __init__(
        self,
        client: SnapdraftMongo,
        doc_type_service: DocumentTypeService,
        file_service: FileService,
        background_tasks: BackgroundTasks,
    ):
        super().__init__(client, "draft", Draft)
        self.background_tasks = background_tasks
        self.doc_type_service = doc_type_service
        self.file_service = file_service
        self.preprocessed_files = BaseCollection(
            client, "preprocessed_file", PreprocessedFile
        )

    async def list_by_doc_type(self, doc_type_id: str) -> ResultList[Draft]:
        cursor = self.collection.find({"doc_type_id": doc_type_id})
        return await self._cursor_to_result_list(cursor)

    async def create(self, doc_type_id: str, draft_create: DraftCreate):
        draft = self._setup_draft(doc_type_id, draft_create)
        draft = await super().create(draft)
        self.background_tasks.add_task(self.preprocess_files, draft)
        return draft

    async def update(self, doc_type_id: str, draft_id: str, draft_create: DraftCreate):
        draft = self._setup_draft(doc_type_id, draft_create)
        draft = await super().update(draft_id, draft)
        self.background_tasks.add_task(self.preprocess_files, draft)
        return draft

    def _setup_draft(self, doc_type_id: str, draft_create: DraftCreate):
        # Really should validate the source files versus what's expected in the doc type here
        return Draft(**{**draft_create.model_dump(), "doc_type_id": doc_type_id})

    async def generate(self, doc_type_id: str, draft_id: str):
        ret = await self.regenerate(doc_type_id, draft_id)
        return GenerateDraftResult(text=ret.text)

    async def regenerate(
        self,
        doc_type_id: str,
        draft_id: str,
        previous_text: str | None = None,
        user_prompt: str | None = None,
    ):
        from snapdraft_server.routes.dependencies import (
            get_generator_name,
            get_generator,
        )

        # doc_type = await self.doc_type_service.get(doc_type_id)
        generator_name = get_generator_name()
        generator = get_generator(generator_name)
        draft = await self.get(draft_id)
        sources = {
            name: await self.get_preprocessed_file(
                name, source_file_id, generator, generator_name
            )
            for name, source_file_id in draft.source_file_ids.items()
        }
        generated = generator.generate(
            template, sources, previous_version=previous_text, user_prompt=user_prompt
        )
        return RegeneratedDraftResult(
            text=generated.markdown, message=generated.explanation_of_changes
        )

    async def preprocess_files(self, draft: Draft):
        logger.info(
            f"Preprocessing {len(draft.source_file_ids)} source files for {draft.id}"
        )
        from snapdraft_server.routes.dependencies import (
            get_generator_name,
            get_generator,
        )

        generator_name = get_generator_name()
        generator = get_generator(generator_name)
        if draft.output_file_id != None:
            output_file = await self.file_service.get(draft.output_file_id)
            if output_file.metadata.extension == "md":
                draft.output_file_md_id = draft.output_file_id
            else:
                parsed_md, original_filename = await self._convert_to_md(
                    generator, draft.output_file_id, "output"
                )
                md_file = await self.file_service.upload_text_file(
                    parsed_md.as_markdown(),
                    StoredFileMetadata(
                        original_filename=original_filename, extension="md"
                    ),
                )
                draft.output_file_md_id = md_file.id
            draft = await super().update(draft.id, draft)
        for name, id in draft.source_file_ids.items():
            await self.get_preprocessed_file(name, id, generator, generator_name)

    async def get_preprocessed_file(
        self,
        source_name: str,
        source_file_id: str,
        generator: DocGenerator,
        generator_name: str,
    ):
        # Use existing file if we have one.
        preprocessed_file = await self.preprocessed_files.collection.find_one(
            {
                "source_file_id": source_file_id,
                "generator_name": generator_name,
                "generator_version": generator.get_version(),
            }
        )
        if preprocessed_file:
            preprocessed_file = self.preprocessed_files.to_model(preprocessed_file)
            path = await self.file_service.get_local_path(
                preprocessed_file.preprocessed_file_id
            )
            preprocessed_data = load_model(path, DocSection)
        else:
            preprocessed_data, original_filename = await self._convert_to_md(
                generator, source_file_id, source_name
            )
            preprocessed_json = json.dumps(preprocessed_data.model_dump())
            preprocessed_file = await self.file_service.upload_text_file(
                preprocessed_json,
                StoredFileMetadata(
                    original_filename=original_filename, extension="json"
                ),
            )
            await self.preprocessed_files.collection.insert_one(
                PreprocessedFile(
                    source_file_id=source_file_id,
                    generator_name=generator_name,
                    generator_version=generator.get_version(),
                    preprocessed_file_id=preprocessed_file.id,
                ).model_dump()
            )
        return preprocessed_data

    async def _convert_to_md(
        self, generator, source_file_id, source_name
    ) -> tuple[DocSection, str]:
        """Converts a file to markdown.  Returns the parsed data and original file name."""
        stored_file = await self.file_service.get(source_file_id)
        saved_file_path = await self.file_service.get_local_path(source_file_id)
        source_file = SourceFile(
            name=source_name,
            original_filename=stored_file.metadata.original_filename,
            path=saved_file_path,
        )
        loop = asyncio.get_running_loop()
        preprocessed_data = await loop.run_in_executor(
            None, lambda: generator.parse_source_file(source_file)
        )
        return preprocessed_data, source_file.original_filename


#
# draft.source_files[0].file_id
# prompt = get_processor_inputs(db, doc_id, inputs, upload_dir)
#
# model = get_dspy_model(db, doc_id, dspy_dir)
# ret = process_narrative(prompt, model)
# return GeneratedDocumentResult(text=ret)


# class RegeneratedDocumentResult(BaseModel):
#     text: str
#     message: str
#
#
# # def get_dspy_model(db, doc_id, dspy_dir):
# #     dspy_model_entry = crud_dspy_model.get_latest_by_doc(db, doc_id)
# #     model = FormatNarrative()
# #     if dspy_model_entry:
# #         logger.info(f"Using DSPy model: {dspy_model_entry.id}")
# #         model.load(dspy_dir / f"{dspy_model_entry.id}.json")
# #     else:
# #         logger.info(f"No model, using 0-shot learning")
# #     return model

# # def preprocess_files(
# #     session_maker: sessionmaker,
# #     doc_id: int,
# #     upload_dir: Path,
# #     dspy_dir: Path,
# # ):
# #     db: Session = session_maker()
# #     logger.info(f"session is {type(db)} {db.__module__} {db.__class__}")
# #     try:
# #         examples = crud_draft.list_by_document_type(db, doc_id)
# #         dspy_examples = []
# #         for example in examples:
# #             try:
# #                 if not example.use_for_training:
# #                     continue
# #                 prompt = get_processor_inputs(db, doc_id, example, upload_dir)
# #                 output_file_path = (
# #                     upload_dir
# #                     / f"{example.output_file.id}.{example.output_file.extension}"
# #                 )
# #                 final_narrative = read_text_file(output_file_path)
# #                 dspy_examples.append(
# #                     dspy.Example(
# #                         patient_profile=prompt,
# #                         final_narrative=final_narrative,
# #                     ).with_inputs("patient_profile")
# #                 )
# #             except Exception as e:
# #                 logger.info(f"Skipping example {example.id}")
# #         model = get_dspy_model(db, doc_id, dspy_dir)
# #         updated_model = optimize_module(model, dspy_examples)
# #         dspy_model_table = DSPyModelTable(
# #             document_type_id=doc_id, num_examples=len(dspy_examples)
# #         )
# #         dspy_model_table = DSPyModelTable.model_validate(dspy_model_table)
# #         logger.info(f"doc id is {doc_id}.  {dspy_model_table}")
# #         model_entry = crud_dspy_model.create(db, dspy_model_table)
# #         logger.info(f"Saving updated model with id {model_entry.id}")
# #         updated_model.save(dspy_dir / f"{model_entry.id}.json")
# #     except Exception as e:
# #         logger.exception("Problem learning new model.  Skipping")
# #     finally:
# #         db.close()
# #
# #
# # def learn_new_model_from_examples(
# #     session_maker: sessionmaker,
# #     doc_id: int,
# #     upload_dir: Path,
# #     dspy_dir: Path,
# # ):
# #     db: Session = session_maker()
# #     logger.info(f"session is {type(db)} {db.__module__} {db.__class__}")
# #     try:
# #         examples = crud_draft.list_by_document_type(db, doc_id)
# #         dspy_examples = []
# #         for example in examples:
# #             try:
# #                 if not example.use_for_training:
# #                     continue
# #                 prompt = get_processor_inputs(db, doc_id, example, upload_dir)
# #                 output_file_path = (
# #                     upload_dir
# #                     / f"{example.output_file.id}.{example.output_file.extension}"
# #                 )
# #                 final_narrative = read_text_file(output_file_path)
# #                 dspy_examples.append(
# #                     dspy.Example(
# #                         patient_profile=prompt,
# #                         final_narrative=final_narrative,
# #                     ).with_inputs("patient_profile")
# #                 )
# #             except Exception as e:
# #                 logger.info(f"Skipping example {example.id}")
# #         model = get_dspy_model(db, doc_id, dspy_dir)
# #         updated_model = optimize_module(model, dspy_examples)
# #         dspy_model_table = DSPyModelTable(
# #             document_type_id=doc_id, num_examples=len(dspy_examples)
# #         )
# #         dspy_model_table = DSPyModelTable.model_validate(dspy_model_table)
# #         logger.info(f"doc id is {doc_id}.  {dspy_model_table}")
# #         model_entry = crud_dspy_model.create(db, dspy_model_table)
# #         logger.info(f"Saving updated model with id {model_entry.id}")
# #         updated_model.save(dspy_dir / f"{model_entry.id}.json")
# #     except Exception as e:
# #         logger.exception("Problem learning new model.  Skipping")
# #     finally:
# #         db.close()
#
#
# # def get_processor_inputs(db, doc_id, inputs, upload_dir):
# #     processor_inputs = {}
# #     for file in inputs.source_files:
# #         stored_file = crud_stored_file.get(db, file.file_id)
# #         doc_type = crud_document_type.get(db, doc_id)
# #         source_doc_type = doc_type.get_source_doc(file.source_document_id)
# #         saved_file_path = upload_dir / f"{stored_file.id}.{stored_file.extension}"
# #         processor_inputs[source_doc_type.name] = (
# #             stored_file.original_filename,
# #             saved_file_path,
# #         )
# #
# #     (
# #         original_filename,
# #         input_file,
# #     ) = processor_inputs["Patient Profile"]
# #     tables = extract_patient_profiles(input_file)
# #     profile = preprocess_patient_profiles(tables)
# #     prompt = input_data_to_str(original_filename, profile)
# #     return prompt
