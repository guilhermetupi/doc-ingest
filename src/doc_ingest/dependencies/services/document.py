from fastapi import Depends

from doc_ingest.dependencies.repositories.document import get_document_repository
from doc_ingest.repositories.interfaces.document import IDocumentRepository
from doc_ingest.services.document import DocumentService
from doc_ingest.services.file_text_parser import FileTextParser
from doc_ingest.services.interface.file_text_parser import IFileTextParser


async def get_file_text_parser() -> IFileTextParser:
    return FileTextParser()

async def get_document_service(
        document_repository: IDocumentRepository = Depends(get_document_repository),
        file_text_parser: IFileTextParser = Depends(get_file_text_parser)
) -> DocumentService:
    return DocumentService(document_repository, file_text_parser)
