from snapdraft_server.services.base.base_collection import BaseCollection
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.services.doc_type_model import DocumentType


class DocumentTypeService(BaseCollection):
    def __init__(self, client: SnapdraftMongo):
        super().__init__(client, "document_type", DocumentType)
