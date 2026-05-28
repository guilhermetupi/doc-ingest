import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doc_ingest.db.database_session import database_session
from doc_ingest.db.models.document import DocumentModel
from doc_ingest.entities.document import Document
from doc_ingest.repositories.interfaces.document import IDocumentRepository
from doc_ingest.repositories.mappers.document import DocumentMapper


class DocumentRepository(IDocumentRepository):
    @database_session
    async def list_documents(self, session: AsyncSession) -> List[Document]:
        stmt = select(DocumentModel).order_by(DocumentModel.created_at.desc())
        result = await session.scalars(stmt)

        entities: List[Document] = []
        for model in result.all():
            entities.append(DocumentMapper.to_entity(model))
        return entities

    @database_session
    async def create_document(self, session: AsyncSession, document: Document) -> Document:
        model = DocumentMapper.to_model(document)
        session.add(model)
        return document

    @database_session
    async def get_document_by_id(self, session: AsyncSession, id: uuid.UUID) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.id == id)
        result = await session.scalars(stmt)
        model = result.one_or_none()
        if model is None:
            return None
        return DocumentMapper.to_entity(model)

