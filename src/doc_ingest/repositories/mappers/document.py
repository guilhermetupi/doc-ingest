from doc_ingest.entities.document import Document
from doc_ingest.db.models.document import DocumentModel

class DocumentMapper:
    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        return DocumentModel(**entity.model_dump())

    @staticmethod
    def to_entity(model: DocumentModel) -> Document:
        return Document.reconstitute(**model.__dict__)
