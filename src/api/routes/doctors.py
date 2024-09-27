from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from service.doctors import DoctorService
from src.api.dto.doctors import CreateDoctorRequest, DoctorDetailsResponse
from src.core.db import get_db_session
from src.schemas.doctors import CreateDoctor

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
)


@router.post(
    path="/",
    summary="Create a new doctor",
    status_code=status.HTTP_201_CREATED,
)
async def create_doctor(
    data: CreateDoctorRequest,
    db: AsyncSession = Depends(get_db_session),
) -> DoctorDetailsResponse:
    data = CreateDoctor(**data.dict())
    doctor = await DoctorService(db=db).create_doctor(data=data)
    await db.commit()
    return DoctorDetailsResponse(**asdict(doctor))


@router.get(
    path="/{id}",
    summary="Get doctor details",
    status_code=status.HTTP_200_OK,
)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> DoctorDetailsResponse:
    doctor = await DoctorService(db=db).get_doctor(
        doctor_id=doctor_id,
        raise_exception=True,
    )
    return DoctorDetailsResponse(**asdict(doctor))


@router.get(
    path="/",
    summary="List all doctors",
    status_code=status.HTTP_200_OK,
)
async def list_doctors(
    db: AsyncSession = Depends(get_db_session),
) -> list[DoctorDetailsResponse]:
    doctors = await DoctorService(db=db).list_doctors()
    return [DoctorDetailsResponse(**asdict(doctor)) for doctor in doctors]
