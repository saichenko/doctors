from sqlalchemy import select

from src.db.models import Doctor
from src.repo.base import RepoBase
from src.schemas.doctors import DoctorInDB


class DoctorRepo(RepoBase):

    model = Doctor

    async def get_by_id(self, id: int) -> DoctorInDB | None:
        stmt = select(self.model).where(self.model.id == id)
        query = await self._db.execute(stmt)
        result = query.scalar_one_or_none()
        if result is None:
            return None
        return result.to_dataclass()

    async def list_doctors(self) -> list[DoctorInDB]:
        result = await self._db.scalars(select(self.model))
        return list(map(lambda d: d.to_dataclass(), result))
