import logging
from typing import Generic, TypeVar, Type

from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel

from snapdraft_server.services.base.result_list import ResultList
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseCollection(Generic[T]):

    def __init__(
        self, client: SnapdraftMongo, collection_name: str, model_class: Type[T]
    ):
        self.client = client
        self.collection_name = collection_name
        self.collection = client.db[collection_name]
        self.model_class = model_class

    @staticmethod
    def dump_no_id(obj: BaseModel):
        return {k: v for k, v in obj.model_dump().items() if k != "id"}

    async def create(
        self,
        obj: T,
    ) -> T:
        model = self.dump_no_id(obj)
        result = await self.collection.insert_one(model)
        if not result.acknowledged:
            raise HTTPException(
                status_code=500, detail=f"Failed to create {self.collection_name}"
            )
        return self.to_model(model)

    async def get(self, id: str) -> T:
        model = await self.collection.find_one({"_id": ObjectId(id)})
        if model is None:
            raise HTTPException(
                status_code=404, detail=f"{self.collection_name} {id} not found"
            )
        return self.to_model(model)

    async def update(self, id: str, obj: T) -> T:
        model = self.dump_no_id(obj)
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": model}
        )
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"{self.collection_name} {id} not found",
            )
        return self.to_model(model, id)

    async def delete(self, id: str) -> dict:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"{self.collection_name} {id} not found"
            )
        return {"status": f"{self.collection_name} {id} deleted"}

    async def to_list(self) -> ResultList[T]:
        cursor = self.collection.find()
        return await self._cursor_to_result_list(cursor)

    def to_model(self, model: dict, id: str | None = None):
        model["id"] = id or str(model["_id"])
        return self.model_class.model_validate(model)

    async def _cursor_to_result_list(self, cursor):
        items = await cursor.to_list(length=None)
        items = [self.to_model(model) for model in items]
        return ResultList[T](items=items)
