from sqlalchemy.ext.asyncio import create_async_engine

from doc_ingest.config.env import settings

if settings.database_url is None:
    raise Exception("database_url cannot be None")

engine = create_async_engine(settings.database_url)

