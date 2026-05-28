import datetime
import uuid
from io import BytesIO
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from doc_ingest.dependencies.services.document import get_document_service
from doc_ingest.entities.document import Document
from doc_ingest.main import app
from doc_ingest.services.document import DocumentService


def create_test_document(**kwargs) -> Document:
    """Helper to build a Document entity with sensible defaults."""
    fields = {
        "name": "test.md",
        "mimetype": "text/markdown",
        "size": 100,
        "text": "content",
    }
    fields.update(kwargs)
    return Document(
        id=fields.pop("id", uuid.uuid4()),
        **fields,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )


@pytest.fixture
def mock_document_service() -> AsyncMock:
    """Return an AsyncMock spec'ed against DocumentService with async stubs."""
    mock = AsyncMock(spec=DocumentService)
    mock.list_documents = AsyncMock()
    mock.create_document = AsyncMock()
    mock.get_document = AsyncMock()
    return mock


@pytest.fixture(autouse=True)
def override_dependencies(mock_document_service: AsyncMock) -> None:
    """Swap the real get_document_service with a lambda returning the mock."""
    app.dependency_overrides[get_document_service] = lambda: mock_document_service
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client() -> AsyncClient:
    """Provide an httpx AsyncClient wired to the FastAPI app via ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# GET /documents/  -- list documents
# ---------------------------------------------------------------------------

class TestListDocuments:
    @pytest.mark.asyncio
    async def test_list_documents(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        docs = [create_test_document(), create_test_document()]
        mock_document_service.list_documents.return_value = docs

        response = await client.get("/documents/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for i, doc in enumerate(docs):
            assert data[i]["id"] == str(doc.id)
            assert data[i]["name"] == doc.name
            assert data[i]["mimetype"] == doc.mimetype
            assert data[i]["size"] == doc.size

    @pytest.mark.asyncio
    async def test_list_documents_empty(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        mock_document_service.list_documents.return_value = []

        response = await client.get("/documents/")

        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# GET /documents/{id}  -- single document
# ---------------------------------------------------------------------------

class TestGetDocument:
    @pytest.mark.asyncio
    async def test_get_document_found(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        doc_id = uuid.uuid4()
        doc = create_test_document(id=doc_id)
        mock_document_service.get_document.return_value = doc

        response = await client.get(f"/documents/{doc_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(doc_id)
        assert data["name"] == doc.name
        assert data["mimetype"] == doc.mimetype
        assert data["size"] == doc.size
        assert data["text"] == doc.text

    @pytest.mark.asyncio
    async def test_get_document_not_found(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        doc_id = uuid.uuid4()
        mock_document_service.get_document.side_effect = HTTPException(
            status_code=404, detail="Document not found"
        )

        response = await client.get(f"/documents/{doc_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"


# ---------------------------------------------------------------------------
# POST /documents/upload  -- create document
# ---------------------------------------------------------------------------

class TestCreateDocument:
    @pytest.mark.asyncio
    async def test_create_document_success(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        doc = create_test_document()
        mock_document_service.create_document.return_value = doc

        file_content = BytesIO(b"# Test markdown content")
        response = await client.post(
            "/documents/upload",
            files={"file": ("test.md", file_content, "text/markdown")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(doc.id)
        assert data["name"] == doc.name
        assert data["mimetype"] == doc.mimetype
        assert data["size"] == doc.size
        assert data["text"] == doc.text

    @pytest.mark.asyncio
    async def test_create_document_too_large(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        mock_document_service.create_document.side_effect = HTTPException(
            status_code=422, detail="File too large"
        )

        file_content = BytesIO(b"x" * 1024 * 1024 * 11)  # 11 MB
        response = await client.post(
            "/documents/upload",
            files={"file": ("large.pdf", file_content, "application/pdf")},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "File too large"

    @pytest.mark.asyncio
    async def test_create_document_unsupported_type(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        mock_document_service.create_document.side_effect = HTTPException(
            status_code=422, detail="Unsupported Content-Type"
        )

        file_content = BytesIO(b"some content")
        response = await client.post(
            "/documents/upload",
            files={"file": ("test.txt", file_content, "text/plain")},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "Unsupported Content-Type"

    @pytest.mark.asyncio
    async def test_create_document_without_file(
        self, client: AsyncClient, mock_document_service: AsyncMock
    ) -> None:
        response = await client.post("/documents/upload")

        assert response.status_code == 422
