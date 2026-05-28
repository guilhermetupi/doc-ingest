from typing import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker

from doc_ingest.db.db import engine


def database_session(func: Callable) -> Callable:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            res = await func(args[0], session, *args[1:], **kwargs)
            await session.commit()
            return res

    return wrapper