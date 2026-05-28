import uuid

import pytest

from doc_ingest.entities.document import Document
from doc_ingest.repositories.document import DocumentRepository


@pytest.fixture
def repo(create_tables):
    return DocumentRepository()


class TestListDocuments:
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_documents(self, repo):
        result = await repo.list_documents()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_all_documents(self, repo):
        doc1 = Document.create(name="a.md", mimetype="text/markdown", size=10, text="a")
        doc2 = Document.create(name="b.pdf", mimetype="application/pdf", size=20, text="b")

        await repo.create_document(document=doc1)
        await repo.create_document(document=doc2)

        result = await repo.list_documents()
        assert len(result) == 2
        assert result[0].id == doc2.id  # more recent first
        assert result[1].id == doc1.id


class TestCreateDocument:
    @pytest.mark.asyncio
    async def test_persists_and_returns_document(self, repo):
        doc = Document.create(name="test.md", mimetype="text/markdown", size=100, text="content")
        result = await repo.create_document(document=doc)

        assert result.id == doc.id
        assert result.name == doc.name
        assert result.mimetype == doc.mimetype
        assert result.size == doc.size
        assert result.text == doc.text

        # Verify it was actually persisted
        fetched = await repo.get_document_by_id(id=doc.id)
        assert fetched is not None
        assert fetched.id == doc.id


class TestGetDocumentById:
    @pytest.mark.asyncio
    async def test_returns_document_when_found(self, repo):
        doc = Document.create(name="found.md", mimetype="text/markdown", size=42, text="hello")
        await repo.create_document(document=doc)

        result = await repo.get_document_by_id(id=doc.id)
        assert result is not None
        assert result.id == doc.id
        assert result.name == "found.md"
        assert result.text == "hello"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, repo):
        result = await repo.get_document_by_id(id=uuid.uuid4())
        assert result is None
