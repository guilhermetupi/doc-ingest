import datetime
import uuid

from sqlalchemy import Uuid, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass

class AuditModel:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))