import typing as t
from dataclasses import asdict, dataclass

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base


class RepoBase:

    model: t.Type[Base]

    def __init__(self, db: AsyncSession):
        self._db: AsyncSession = db

    async def create(self, data: dataclass, *args, **kwargs) -> dataclass:
        """Insert new row by providing data."""
        stmt = insert(self.model).values(**asdict(data)).returning(self.model)
        query = await self._db.execute(stmt)
        result = query.scalar_one()
        return result.to_dataclass()
