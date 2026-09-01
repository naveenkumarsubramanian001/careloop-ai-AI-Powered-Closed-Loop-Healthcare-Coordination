from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentResponse


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    async def create(
        self,
        document: DocumentResponse,
    ) -> DocumentResponse:

        db_document = Document(
            id=document.id,
            patient_id=document.patient_id,
            filename=document.filename,
            content_type=document.content_type,
            size=document.size,
            storage_key=document.storage_key,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)

        return DocumentResponse.model_validate(db_document)

    async def get_by_id(
        self,
        document_id: str,
    ) -> DocumentResponse | None:

        statement = select(Document).where(
            Document.id == document_id
        )

        result = self.db.execute(statement)

        document = result.scalar_one_or_none()

        if document is None:
            return None

        return DocumentResponse.model_validate(document)

    async def get_by_patient_id(
        self,
        patient_id: str,
    ) -> list[DocumentResponse]:

        statement = (
            select(Document)
            .where(Document.patient_id == patient_id)
            .order_by(Document.created_at.desc())
        )

        result = self.db.execute(statement)

        documents = result.scalars().all()

        return [
            DocumentResponse.model_validate(document)
            for document in documents
        ]

    async def delete(
        self,
        document_id: str,
    ) -> bool:

        statement = select(Document).where(
            Document.id == document_id
        )

        result = self.db.execute(statement)

        document = result.scalar_one_or_none()

        if document is None:
            return False

        self.db.delete(document)
        self.db.commit()

        return True