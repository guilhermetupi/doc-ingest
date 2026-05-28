import uuid
from typing import List

from fastapi import UploadFile, HTTPException

from doc_ingest.entities.document import Document
from doc_ingest.repositories.interfaces.document import IDocumentRepository
from doc_ingest.services.interface.file_text_parser import IFileTextParser


class DocumentService:
    def __init__(self, document_repository: IDocumentRepository, file_text_parser: IFileTextParser):
        self.document_repository = document_repository
        self.file_text_parser = file_text_parser

    async def list_documents(self) -> List[Document]:
        return await self.document_repository.list_documents()

    async def create_document(self, file: UploadFile) -> Document:
        name = file.filename
        size = file.size
        mimetype = file.content_type

        if size > 10 * 1024 * 1024:
            raise HTTPException(422, 'File too large')

        if mimetype not in ('application/pdf', 'text/markdown'):
            raise HTTPException(422, 'Unsupported Content-Type')

        text = await self.file_text_parser.parse(file)

        document = Document.create(
            name=name,
            size=size,
            mimetype=mimetype,
            text=text,
        )
        return await self.document_repository.create_document(document)

    async def get_document(self, id: uuid.UUID) -> Document:
        document = await self.document_repository.get_document_by_id(id)
        if document is None:
            raise HTTPException(404, 'Document not found')
        return document