import uuid
import datetime

from doc_ingest.entities.document import Document
from doc_ingest.repositories.mappers.document import DocumentMapper


class TestDocumentMapper:
    """Tests for the DocumentMapper."""

    def test_to_model(self):
        """to_model should convert a Document entity to a DocumentModel with matching fields."""
        entity = Document.create(
            name="test.pdf",
            mimetype="application/pdf",
            size=1024,
            text="Hello, world!",
        )

        model = DocumentMapper.to_model(entity)

        assert model.id == entity.id
        assert model.name == entity.name
        assert model.mimetype == entity.mimetype
        assert model.size == entity.size
        assert model.text == entity.text
        assert model.created_at == entity.created_at
        assert model.updated_at == entity.updated_at

    def test_to_entity(self):
        """to_entity should convert a DocumentModel to a Document entity with matching fields."""
        doc_id = uuid.uuid4()
        now = datetime.datetime.now()

        class FakeColumn:
            def __init__(self, name):
                self.name = name

        class FakeTable:
            def __init__(self, columns):
                self.columns = columns

        class FakeModel:
            pass

        fields = {
            "id": doc_id,
            "name": "report.pdf",
            "mimetype": "application/pdf",
            "size": 2048,
            "text": "Report content",
            "created_at": now,
            "updated_at": now,
        }

        model = FakeModel()
        model.__table__ = FakeTable([FakeColumn(name) for name in fields])
        for name, value in fields.items():
            setattr(model, name, value)

        entity = DocumentMapper.to_entity(model)

        assert entity.id == doc_id
        assert entity.name == "report.pdf"
        assert entity.mimetype == "application/pdf"
        assert entity.size == 2048
        assert entity.text == "Report content"
        assert entity.created_at == now
        assert entity.updated_at == now
