from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from doc_ingest.db.models.base import AuditModel, BaseModel


class DocumentModel(AuditModel, BaseModel):
    __tablename__ = "documents"

    name: Mapped[str] = mapped_column(String(256))
    mimetype: Mapped[str] = mapped_column(String(256))
    size: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
