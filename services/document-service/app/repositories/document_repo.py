import uuid
from typing import Dict, Any

# Mock Document Repository for Postgres
class DocumentRepository:
    def __init__(self):
        # In memory storage for the mock
        self.documents = {}

    def create_document(self, patient_id: str, file_name: str, storage_path: str) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        doc = {
            "id": doc_id,
            "patient_id": patient_id,
            "file_name": file_name,
            "storage_path": storage_path,
            "status": "uploaded"
        }
        self.documents[doc_id] = doc
        return doc

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        return self.documents.get(doc_id)

    def get_patient_documents(self, patient_id: str) -> list[Dict[str, Any]]:
        return [d for d in self.documents.values() if d["patient_id"] == patient_id]

    def delete_document(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]

document_repo = DocumentRepository()
