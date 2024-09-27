from sqlalchemy.ext.asyncio import AsyncSession


class ServiceBase:

    def __init__(self, db: AsyncSession):
        self._db = db
