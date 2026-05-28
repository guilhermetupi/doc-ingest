from doc_ingest.repositories.interfaces.document import IDocumentRepository
from doc_ingest.repositories.document import DocumentRepository


async def get_document_repository() -> IDocumentRepository:
    return DocumentRepository()