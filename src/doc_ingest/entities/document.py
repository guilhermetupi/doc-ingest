import datetime
import uuid

from pydantic import BaseModel


class Document(BaseModel):
    id: uuid.UUID
    name: str
    mimetype: str
    size: int
    text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @staticmethod
    def create(
            name: str,
            mimetype: str,
            size: int,
            text: str,
    ):
        return Document(
            id=uuid.uuid4(),
            name=name,
            mimetype=mimetype,
            size=size,
            text=text,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

    @staticmethod
    def reconstitute(
            id: str,
            name: str,
            mimetype: str,
            size: int,
            text: str,
            created_at: datetime.datetime,
            updated_at: datetime.datetime,
    ):
        return Document(
            id=id,
            name=name,
            mimetype=mimetype,
            size=size,
            text=text,
            created_at=created_at,
            updated_at=updated_at,
        )

