from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from snapdraft_server.services.draft_model import (
    DraftCreate,
    Draft,
    GenerateDraftResult,
    RegeneratedDraftResult,
)
from snapdraft_server.services.doc_type_model import DocumentType
from snapdraft_server.services.doc_type_service import DocumentTypeService
from snapdraft_server.routes.dependencies import (
    get_doc_type_service,
    get_draft_service,
    get_model_service,
    get_file_service,
    get_generator,
    get_generator_name,
)
from snapdraft_server.services.base.result_list import ResultList
from snapdraft_server.services.draft_service import (
    DraftService,
)
from snapdraft_server.services.file_service import FileService
from snapdraft_server.services.model_model import Model, ModelCreate
from snapdraft_server.services.model_service import ModelService

logger = logging.getLogger(__name__)

# Router
router = APIRouter()


# Routes for Document Types and Drafts
@router.post("/", response_model=DocumentType, operation_id="create_document_type")
async def create_document_type(
    document: DocumentType,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
) -> DocumentType:
    return await doc_type_service.create(document)


@router.get(
    "/{doc_id}",
    response_model=DocumentType,
    operation_id="read_document_type",
)
async def read_document_type(
    doc_id: str,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
) -> DocumentType:
    return await doc_type_service.get(doc_id)


@router.put(
    "/{doc_id}",
    response_model=DocumentType,
    operation_id="update_document_type",
)
async def update_document_type(
    doc_id: str,
    document: DocumentType,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
) -> DocumentType:
    return await doc_type_service.update(doc_id, document)


@router.delete("/{doc_id}", response_model=dict, operation_id="delete_document_type")
async def delete_document_type(
    doc_id: str,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
):
    return await doc_type_service.delete(doc_id)


@router.get(
    "/",
    response_model=ResultList[DocumentType],
    operation_id="read_all_document_types",
)
async def read_all_document_types(
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
) -> ResultList[DocumentType]:
    docs = await doc_type_service.to_list()
    return docs


@router.post(
    "/{doc_id}/drafts/",
    response_model=Draft,
    operation_id="create_draft",
)
async def create_draft(
    doc_id: str,
    draft: DraftCreate,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.create(doc_id, draft)


@router.get(
    "/{doc_id}/drafts/{draft_id}",
    response_model=Draft,
    operation_id="read_draft",
)
async def read_draft(
    doc_id: str,
    draft_id: str,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.get(draft_id)


@router.get(
    "/{doc_id}/drafts/{draft_id}/source/{source}/preprocessed",
    operation_id="read_draft_preprocessed_source",
)
async def read_draft_preprocessed_source(
    doc_id: str,
    draft_id: str,
    source: str,
    draft_service: DraftService = Depends(get_draft_service),
) -> str:
    draft = await draft_service.get(draft_id)
    generator_name = get_generator_name()
    generator = get_generator(generator_name)
    preprocessed_data = await draft_service.get_preprocessed_file(
        source, draft.source_file_ids[source], generator, generator_name
    )
    return preprocessed_data.as_markdown()


@router.put(
    "/{doc_id}/drafts/{draft_id}",
    response_model=Draft,
    operation_id="update_draft",
)
async def update_draft(
    doc_id: str,
    draft_id: str,
    draft: DraftCreate,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.update(doc_id, draft_id, draft)


@router.delete(
    "/{doc_id}/drafts/{draft_id}",
    response_model=dict,
    operation_id="delete_draft",
)
async def delete_draft(
    doc_id: str,
    draft_id: str,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.delete(draft_id)


@router.get(
    "/{doc_id}/drafts/",
    response_model=ResultList[Draft],
    operation_id="read_all_drafts",
)
async def read_all_drafts(
    doc_id: str,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
    draft_service: DraftService = Depends(get_draft_service),
):
    # Get the doc type to differentiate between a non-existing doc type and an empty list.
    doc_type = await doc_type_service.get(doc_id)
    return await draft_service.list_by_doc_type(doc_id)


@router.post(
    "/{doc_id}/drafts/{draft_id}/generate",
    response_model=GenerateDraftResult,
    operation_id="generate_draft",
)
async def generate_draft(
    doc_id: str,
    draft_id: str,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.generate(doc_id, draft_id)


@router.post(
    "/{doc_id}/drafts/{draft_id}/regenerate",
    response_model=RegeneratedDraftResult,
    operation_id="regenerate_draft",
)
async def regenerate_draft(
    doc_id: str,
    draft_id: str,
    previous_text: str,
    user_prompt: str,
    draft_service: DraftService = Depends(get_draft_service),
):
    return await draft_service.regenerate(doc_id, draft_id, previous_text, user_prompt)


@router.get(
    "/{doc_id}/models/",
    response_model=ResultList[Model],
    operation_id="read_all_models",
)
async def read_all_models(
    doc_id: str,
    doc_type_service: DocumentTypeService = Depends(get_doc_type_service),
    model_service: ModelService = Depends(get_model_service),
):
    # Get the doc type to differentiate between a non-existing doc type and an empty list.
    doc_type = await doc_type_service.get(doc_id)
    return await model_service.list_by_doc_type(doc_id)


@router.post(
    "/{doc_id}/models/{model_id}/default",
    response_model=Model,
    operation_id="set_active_model",
)
async def set_active_model(
    doc_id: str,
    model_id: str,
    model_service: ModelService = Depends(get_model_service),
):
    return await model_service.set_active_model(doc_id, model_id)


@router.post(
    "/{doc_id}/models/",
    response_model=Model,
    operation_id="create_model",
)
async def create_model(
    doc_id: str,
    model: ModelCreate,
    model_service: ModelService = Depends(get_model_service),
):
    return await model_service.create_new_model(doc_id, model)


@router.delete(
    "/{doc_id}/models/{model_id}",
    response_model=dict,
    operation_id="delete_model",
)
async def delete_model(
    doc_id: str,
    model_id: str,
    model_service: ModelService = Depends(get_model_service),
):
    return await model_service.delete(model_id)
