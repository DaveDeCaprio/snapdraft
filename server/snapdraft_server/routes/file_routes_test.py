import io
import logging

import pytest

from snapdraft_server.routes.app_fixture import client

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_stored_file(client):
    async with client as ac:
        file_content = io.BytesIO(b"Test file content")
        file_content.name = "test_file.txt"

        # Simulate the upload
        files = {"file": (file_content.name, file_content, "text/plain")}
        response = await ac.post("/files/upload/", files=files, follow_redirects=True)

        # Assertions to verify the response
        logger.info(f"Response: {response.headers}")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response: {data}")
        assert data["id"] is not None
        assert data["metadata"]["original_filename"] == "test_file.txt"
