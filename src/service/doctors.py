from exceptions import DoctorNotFoundError
from repo.doctors import DoctorRepo
from src.schemas.doctors import CreateDoctor, DoctorInDB
from src.service.base import ServiceBase


class DoctorService(ServiceBase):

    def __init__(self, *args, **kwargs):
        super(DoctorService, self).__init__(*args, **kwargs)
        self.__doctor_repo = DoctorRepo(db=self._db)

    async def create_doctor(self, data: CreateDoctor) -> DoctorInDB:
        return await self.__doctor_repo.create(data)

    async def get_doctor(
        self,
        doctor_id: int,
        raise_exception: bool = False,
    ) -> DoctorInDB | None:
        doctor = await self.__doctor_repo.get_by_id(id=doctor_id)
        if doctor is None and raise_exception is True:
            raise DoctorNotFoundError
        return doctor

    async def list_doctors(self) -> list[DoctorInDB]:
        return await self.__doctor_repo.list_doctors()
