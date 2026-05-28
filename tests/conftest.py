import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"

from sqlalchemy.pool import StaticPool

import sqlalchemy.ext.asyncio as _sa_async

_original_create = _sa_async.create_async_engine


def _patched_create(url, **kwargs):
    kwargs.setdefault("poolclass", StaticPool)
    return _original_create(url, **kwargs)


_sa_async.create_async_engine = _patched_create

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from doc_ingest.db.db import engine
from doc_ingest.db.models.base import BaseModel
from doc_ingest.db.models.document import DocumentModel


@pytest_asyncio.fixture(scope="session")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_table(create_tables):
    """Delete all rows after each test so tests don't leak data between each other."""
    yield
    async with engine.begin() as conn:
        await conn.execute(delete(DocumentModel))


@pytest_asyncio.fixture
async def async_session(create_tables):
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    async with session_factory() as session:
        yield session
        await session.rollback()
        await session.close()
