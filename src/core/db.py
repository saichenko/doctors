import contextlib
import typing as t
from dataclasses import dataclass
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class Base(DeclarativeBase):

    def to_dataclass(self) -> t.Type[dataclass]:
        """Converts orm model to dataclass instance."""
        raise NotImplementedError


class DatabaseSessionManager:
    def __init__(
        self,
        host: str,
        engine_kwargs: dict[str, Any] | None = None,
    ):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
        )

    async def close(self):
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(
    settings.get_database_uri(),
    {"echo": settings.POSTGRES_ECHO},
)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
