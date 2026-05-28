import uuid
from http.client import HTTPException

from fastapi import APIRouter, Depends, UploadFile, File

from doc_ingest.dependencies.services.document import get_document_service
from doc_ingest.services.document import DocumentService

document_router = APIRouter(prefix='/documents', tags=["document"])

@document_router.get('/')
async def list_documents(document_service:  DocumentService = Depends(get_document_service)):
    return await document_service.list_documents()

@document_router.post('/upload')
async def create_document(
        file: UploadFile = File(...),
        document_service: DocumentService = Depends(get_document_service)
):
  return await document_service.create_document(file)

@document_router.get('/{id}')
async def get_document(id: uuid.UUID, document_service: DocumentService = Depends(get_document_service)):
    return await document_service.get_document(id)