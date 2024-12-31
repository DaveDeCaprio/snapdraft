import io
import logging

import pytest

from snapdraft_server.routes.app_fixture import client

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_document_type(client):
    async with client as ac:
        response = await ac.post("/document-types/", json={"name": "Test Document"})
        assert response.status_code == 200
        data = response.json()
        logger.info(data)
        assert data["id"] is not None
        assert data["name"] == "Test Document"


@pytest.mark.asyncio
async def test_read_document_type(client):
    async with client as ac:
        # Create document first
        response = await ac.post("/document-types/", json={"name": "Test Document"})
        document_id = response.json()["id"]

        # Now read the document
        response = await ac.get(f"/document-types/{document_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == document_id
        assert data["name"] == "Test Document"


@pytest.mark.asyncio
async def test_update_document_type(client):
    async with client as ac:
        # Create document first
        response = await ac.post("/document-types/", json={"name": "Old Document"})
        document_id = response.json()["id"]

        # Update the document
        response = await ac.put(
            f"/document-types/{document_id}", json={"name": "Updated Document"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Document"


@pytest.mark.asyncio
async def test_delete_document_type(client):
    async with client as ac:
        # Create document first
        response = await ac.post(
            "/document-types/", json={"name": "Document to Delete"}
        )
        document_id = response.json()["id"]

        # Delete the document
        response = await ac.delete(f"/document-types/{document_id}")
        assert response.status_code == 200

        # Try to read deleted document
        response = await ac.get(f"/document-types/{document_id}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_all_document_types(client):
    async with client as ac:
        # Create document first
        response = await ac.post(
            "/document-types/", json={"name": "Document to Delete"}
        )
        document_id = response.json()["id"]

        response = await ac.get(f"/document-types/")
        assert response.status_code == 200
        result_list = response.json()
        assert len(result_list["items"]) == 1


# Need to mock preprocessing appropriately
# @pytest.mark.asyncio
# async def test_create_draft_doc(client):
#     async with client as ac:
#         response = await ac.post(
#             "/document-types/",
#             json={
#                 "name": "Test Document",
#                 "sources": [{"name": "source1", "description": "The source"}],
#             },
#         )
#         resp_json = response.json()
#         document_id = resp_json["id"]
#         source_doc_name = resp_json["sources"][0]["name"]
#         assert source_doc_name == "source1"
#
#         file_content = io.BytesIO(b"Test file content")
#         file_content.name = "test_file.txt"
#         files = {"file": (file_content.name, file_content, "text/plain")}
#         response = await ac.post("/files/upload/", files=files, follow_redirects=True)
#         assert response.status_code == 200
#         data = response.json()
#         file_id = data["id"]
#
#         response = await ac.post(
#             f"/document-types/{document_id}/drafts/",
#             json={
#                 "name": "Example Document",
#                 "output_file_id": file_id,
#                 "source_file_ids": {
#                     "source1": file_id,
#                 },
#                 "use_for_training": True,
#             },
#         )
#         logger.info(f"Create draft returned {response.text}")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["id"] is not None
#         assert data["source_file_ids"]["source1"] == file_id
#         logger.info("Finished creating draft document")
