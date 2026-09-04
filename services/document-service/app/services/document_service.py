from datetime import datetime, timezone
import logging
from pathlib import PurePath
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse
from app.storage.minio_client import MinioStorage

logger = logging.getLogger(__name__)


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

    @staticmethod
    def _safe_filename(filename: str) -> str:
        safe_name = PurePath(filename).name.strip()
        if not safe_name or safe_name in {".", ".."}:
            raise ValueError("Filename is invalid.")
        return safe_name

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
        safe_filename = self._safe_filename(file.filename)

        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Unsupported file type: {file.content_type}")

        file_content = await file.read()
        file_size = len(file_content)

        if file_size == 0:
            raise ValueError("File is empty.")

        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError("File is too large.")

        document_id = f"doc_{uuid4().hex[:12]}"
        normalized_patient_id = patient_id.strip()
        storage_key = f"patients/{normalized_patient_id}/{document_id}/{safe_filename}"
        now = datetime.now(timezone.utc)

        document = DocumentResponse(
            id=document_id,
            patient_id=normalized_patient_id,
            filename=safe_filename,
            content_type=file.content_type,
            size=file_size,
            storage_key=storage_key,
            status="uploaded",
            created_at=now,
            updated_at=now,
        )

        try:
            self.storage.ensure_bucket_exists()
            await self.storage.upload(storage_key, file_content, file.content_type)
            db = self._get_db()
            repository = DocumentRepository(db)
            created = await repository.create(document)
            logger.info(
                "document_uploaded",
                extra={"document_id": document_id, "patient_id": normalized_patient_id, "size": file_size},
            )
            return created
        except Exception as exc:
            logger.exception("document_upload_failed", extra={"document_id": document_id, "patient_id": normalized_patient_id})
            try:
                await self.storage.delete(storage_key)
            except Exception as cleanup_exc:
                logger.warning("document_upload_cleanup_failed", exc_info=cleanup_exc, extra={"storage_key": storage_key})
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
            deleted = await repository.delete(document_id)
            if deleted:
                logger.info("document_deleted", extra={"document_id": document_id})
            return deleted
        finally:
            db.close()
