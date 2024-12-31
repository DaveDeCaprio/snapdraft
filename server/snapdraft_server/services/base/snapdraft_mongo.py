from __future__ import annotations
from typing import Generator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


class SnapdraftMongo:
    def __init__(
        self,
        client: AsyncIOMotorClient,
        database_name: str,
        gridfs_client_class=AsyncIOMotorGridFSBucket,
    ):
        self.client = client
        self.db = self.client[database_name]
        self.gridfs = gridfs_client_class(self.db)

    async def close(self):
        self.client.close()
