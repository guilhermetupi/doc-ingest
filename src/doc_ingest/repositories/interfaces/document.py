import uuid
from abc import ABC, abstractmethod
from typing import List

from doc_ingest.entities.document import Document


class IDocumentRepository(ABC):
    @abstractmethod
    async def list_documents(self) -> List[Document]:
        pass

    @abstractmethod
    async def create_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def get_document_by_id(self, id: uuid.UUID) -> Document | None:
        pass