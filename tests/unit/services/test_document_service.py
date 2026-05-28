import uuid
import datetime
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import HTTPException, UploadFile

from doc_ingest.entities.document import Document
from doc_ingest.services.document import DocumentService
from doc_ingest.repositories.interfaces.document import IDocumentRepository
from doc_ingest.services.interface.file_text_parser import IFileTextParser


@pytest.fixture
def mock_repo():
    return MagicMock(spec=IDocumentRepository)


@pytest.fixture
def mock_parser():
    return MagicMock(spec=IFileTextParser)


@pytest.fixture
def service(mock_repo, mock_parser):
    return DocumentService(mock_repo, mock_parser)


class TestListDocuments:
    @pytest.mark.asyncio
    async def test_list_documents(self, service, mock_repo):
        doc1 = Document.create(name="doc1", mimetype="text/markdown", size=100, text="content1")
        doc2 = Document.create(name="doc2", mimetype="application/pdf", size=200, text="content2")
        mock_repo.list_documents = AsyncMock(return_value=[doc1, doc2])

        result = await service.list_documents()

        assert len(result) == 2
        assert result == [doc1, doc2]
        mock_repo.list_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, service, mock_repo):
        mock_repo.list_documents = AsyncMock(return_value=[])

        result = await service.list_documents()

        assert result == []
        mock_repo.list_documents.assert_called_once()


class TestGetDocument:
    @pytest.mark.asyncio
    async def test_get_document_found(self, service, mock_repo):
        doc_id = uuid.uuid4()
        now = datetime.datetime.now()
        doc = Document.reconstitute(
            id=doc_id, name="doc", mimetype="text/markdown",
            size=100, text="content", created_at=now, updated_at=now,
        )
        mock_repo.get_document_by_id = AsyncMock(return_value=doc)

        result = await service.get_document(doc_id)

        assert result == doc
        mock_repo.get_document_by_id.assert_called_once_with(doc_id)

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, service, mock_repo):
        doc_id = uuid.uuid4()
        mock_repo.get_document_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_document(doc_id)

        assert exc_info.value.status_code == 404
        mock_repo.get_document_by_id.assert_called_once_with(doc_id)


class TestCreateDocument:
    @pytest.mark.asyncio
    async def test_create_document_success(self, service, mock_repo, mock_parser):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.md"
        file.size = 100
        file.content_type = "text/markdown"

        mock_parser.parse = AsyncMock(return_value="parsed text")

        created_doc = Document.create(
            name="test.md", mimetype="text/markdown", size=100, text="parsed text"
        )
        mock_repo.create_document = AsyncMock(return_value=created_doc)

        result = await service.create_document(file)

        assert isinstance(result, Document)
        assert result.name == "test.md"
        assert result.mimetype == "text/markdown"
        assert result.size == 100
        assert result.text == "parsed text"
        mock_parser.parse.assert_called_once_with(file)
        mock_repo.create_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_document_too_large(self, service, mock_repo, mock_parser):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.md"
        file.size = 20 * 1024 * 1024
        file.content_type = "text/markdown"

        with pytest.raises(HTTPException) as exc_info:
            await service.create_document(file)

        assert exc_info.value.status_code == 422
        assert "File too large" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_document_unsupported_type(self, service, mock_repo, mock_parser):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.png"
        file.size = 100
        file.content_type = "image/png"

        with pytest.raises(HTTPException) as exc_info:
            await service.create_document(file)

        assert exc_info.value.status_code == 422
        assert "Unsupported Content-Type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_document_pdf(self, service, mock_repo, mock_parser):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.pdf"
        file.size = 100
        file.content_type = "application/pdf"

        mock_parser.parse = AsyncMock(return_value="pdf text content")

        created_doc = Document.create(
            name="test.pdf", mimetype="application/pdf", size=100, text="pdf text content"
        )
        mock_repo.create_document = AsyncMock(return_value=created_doc)

        result = await service.create_document(file)

        assert isinstance(result, Document)
        assert result.mimetype == "application/pdf"
        assert result.text == "pdf text content"
        mock_parser.parse.assert_called_once_with(file)
        mock_repo.create_document.assert_called_once()
