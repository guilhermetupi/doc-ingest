import uuid
import datetime

from pydantic import BaseModel

from doc_ingest.entities.document import Document


class TestDocumentEntity:
    """Tests for the Document entity."""

    def test_create(self):
        """Document.create() should return a Document with correct fields."""
        doc = Document.create(
            name="test.pdf",
            mimetype="application/pdf",
            size=1024,
            text="Hello, world!",
        )

        assert doc.name == "test.pdf"
        assert doc.mimetype == "application/pdf"
        assert doc.size == 1024
        assert doc.text == "Hello, world!"
        assert isinstance(doc.id, uuid.UUID)
        assert isinstance(doc.created_at, datetime.datetime)
        assert isinstance(doc.updated_at, datetime.datetime)

    def test_create_different_ids(self):
        """Two calls to Document.create() should produce different IDs."""
        doc1 = Document.create(
            name="a.pdf", mimetype="application/pdf", size=1, text="a"
        )
        doc2 = Document.create(
            name="b.pdf", mimetype="application/pdf", size=2, text="b"
        )

        assert doc1.id != doc2.id

    def test_reconstitute(self):
        """Document.reconstitute() should return a Document with all fields matching the input."""
        doc_id = uuid.uuid4()
        now = datetime.datetime.now()

        doc = Document.reconstitute(
            id=doc_id,
            name="test.pdf",
            mimetype="application/pdf",
            size=1024,
            text="Hello, world!",
            created_at=now,
            updated_at=now,
        )

        assert doc.id == doc_id
        assert doc.name == "test.pdf"
        assert doc.mimetype == "application/pdf"
        assert doc.size == 1024
        assert doc.text == "Hello, world!"
        assert doc.created_at == now
        assert doc.updated_at == now

    def test_document_is_pydantic_model(self):
        """Document should be a Pydantic BaseModel and support model_dump()."""
        doc = Document.create(
            name="t.pdf", mimetype="text/plain", size=0, text=""
        )

        assert isinstance(doc, BaseModel)

        data = doc.model_dump()
        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data
        assert "mimetype" in data
        assert "size" in data
        assert "text" in data
        assert "created_at" in data
        assert "updated_at" in data
