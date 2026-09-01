from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse
from app.storage.minio_client import MinioStorage


class DocumentService:
    """Business logic for document management."""

    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "text/plain",
    }

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    def __init__(self):
        self.storage = MinioStorage()

    def _get_db(self) -> Session:
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise

    async def upload_document(self, patient_id: str, file: UploadFile) -> DocumentResponse:
        if not patient_id or not patient_id.strip():
            raise ValueError("Patient ID is required.")

        if not file.filename:
            raise ValueError("Filename is required.")

        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Unsupported file type: {file.content_type}")

        file_content = await file.read()
        file_size = len(file_content)

        if file_size == 0:
            raise ValueError("File is empty.")

        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError("File is too large.")

        document_id = f"doc_{uuid4().hex[:12]}"
        storage_key = f"patients/{patient_id}/{document_id}/{file.filename}"
        now = datetime.now(timezone.utc)

        document = DocumentResponse(
            id=document_id,
            patient_id=patient_id,
            filename=file.filename,
            content_type=file.content_type,
            size=file_size,
            storage_key=storage_key,
            status="uploaded",
            created_at=now,
            updated_at=now,
        )

        try:
            await self.storage.upload(storage_key, file_content, file.content_type)
            db = self._get_db()
            repository = DocumentRepository(db)
            return await repository.create(document)
        except Exception:
            try:
                await self.storage.delete(storage_key)
            except Exception:
                pass
            raise
        finally:
            if "db" in locals():
                db.close()

    async def get_document(self, document_id: str) -> DocumentResponse | None:
        db = self._get_db()
        try:
            repository = DocumentRepository(db)
            return await repository.get_by_id(document_id)
        finally:
            db.close()

    async def get_patient_documents(self, patient_id: str) -> list[DocumentResponse]:
        db = self._get_db()
        try:
            repository = DocumentRepository(db)
            return await repository.get_by_patient_id(patient_id)
        finally:
            db.close()

    async def delete_document(self, document_id: str) -> bool:
        db = self._get_db()
        try:
            repository = DocumentRepository(db)
            document = await repository.get_by_id(document_id)
            if document is None:
                return False

            await self.storage.delete(document.storage_key)
            return await repository.delete(document_id)
        finally:
            db.close()