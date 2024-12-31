import logging
import shutil
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from snapdraft_server.services.base.mock_gridfs import MockAsyncIOMotorGridFSBucket
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.routes.app_setup import create_app

logger = logging.getLogger(__name__)


@pytest.fixture()
def client(mongodb):
    snapdraft_mongo = SnapdraftMongo(
        AsyncMongoMockClient(),
        "snapdraft_unittest",
        MockAsyncIOMotorGridFSBucket(Path("./output/tests/gridfs")),
    )

    origins = [
        "http://localhost:3000",  # Replace with the port your React app is running on
        "http://localhost:5173",  # Adjust as per your Vite setup
    ]
    local_cache_dir = Path("./output/tests/local_cache")
    shutil.rmtree(local_cache_dir, ignore_errors=True)
    local_cache_dir.mkdir(parents=True, exist_ok=True)
    dspy_dir = Path("./output/tests/dspy")
    shutil.rmtree(dspy_dir, ignore_errors=True)
    dspy_dir.mkdir(parents=True, exist_ok=True)
    app = create_app(
        origins, snapdraft_mongo, local_cache_dir=local_cache_dir, dspy_dir=dspy_dir
    )

    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    logger.info("Shutting down client")
    snapdraft_mongo.close()
