import asyncio
import logging
from http.client import HTTPException

from fastapi import BackgroundTasks

from snapdraft_server.services.base.base_collection import BaseCollection
from snapdraft_server.services.base.result_list import ResultList
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.services.doc_type_service import DocumentTypeService
from snapdraft_server.services.draft_service import DraftService
from snapdraft_server.services.file_service import FileService
from snapdraft_server.services.model_model import Model, ModelCreate

logger = logging.getLogger(__name__)


class ModelService(BaseCollection):
    def __init__(
        self,
        client: SnapdraftMongo,
        doc_type_service: DocumentTypeService,
        file_service: FileService,
        draft_service: DraftService,
        background_tasks: BackgroundTasks,
    ):
        super().__init__(client, "model", Model)
        self.doc_type_service = doc_type_service
        self.file_service = file_service
        self.draft_service = draft_service
        self.background_tasks = background_tasks

    async def list_by_doc_type(self, doc_type_id: str) -> ResultList[Model]:
        cursor = self.collection.find({"doc_type_id": doc_type_id})
        results = await self._cursor_to_result_list(cursor)
        logger.info(f"Models: {results}")
        if len(results.items) == 0:
            default = await self.create_default_model(doc_type_id)
            results = ResultList(items=[default])
        return results

    async def create_default_model(self, doc_type_id: str) -> Model:
        default_model = Model(
            doc_type_id=doc_type_id,
            version="Default Model",
            status="Ready",
            is_active=True,
        )
        default_model = await self.create(default_model)
        return default_model

    async def create_new_model(
        self, doc_type_id: str, model_create: ModelCreate
    ) -> Model:
        existing_models = await self.list_by_doc_type(doc_type_id)
        version = f"v{len(existing_models.items)+1}"
        drafts = await self.draft_service.list_by_doc_type(doc_type_id)
        draft_ids = [_.id for _ in drafts.items if _.use_for_training]
        new_model = Model(
            doc_type_id=doc_type_id,
            version=version,
            generator=model_create.generator,
            status="Training",
            draft_ids=draft_ids,
        )
        new_model = await self.create(new_model)
        self.background_tasks.add_task(self.train_model, new_model)
        return new_model

    async def train_model(self, model: Model):
        logger.info(f"Training model {model.id}")
        await asyncio.sleep(5)
        model.status = "Ready"
        await self.update(model.id, model)

    async def delete(self, id: str) -> dict:
        model = await self.get(id)
        if model.is_active:
            raise HTTPException(
                status_code=400, detail=f"Can't delete the active model"
            )
        return await super().delete(id)

    async def set_active_model(self, doc_id: str, model_id: str) -> dict:
        existing_active = await self.collection.find_one(
            {"doc_id": doc_id, "is_active": True}
        )
        if existing_active:
            existing_active.is_active = False
            await self.collection.replace_one(
                {"_id": existing_active.id}, existing_active.dict()
            )

        model = await self.get(model_id)
        model.is_active = True
        return await self.update(model_id, model)
