import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.db import get_db_session
from src.api.dto.appointments import CreateAppointmentRule
from src.schemas.appointment import CreateAppointment
from src.service.appointments import AppointmentService

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post(
    path="/",
    summary="Create new appointment rule",
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    data: CreateAppointmentRule,
    db: AsyncSession = Depends(get_db_session),
):
    create_appointment_data = CreateAppointment(**data.dict())
    appointment = await AppointmentService(db=db).create_appointment(
        data=create_appointment_data,
    )
    await db.commit()
    return appointment


@router.get(
    path="/free-intervals/{doctor_id}",
    summary="List appointment free intervals.",
    status_code=status.HTTP_201_CREATED,
)
async def get_free_intervals(
    doctor_id: int,
    since: dt.date,
    until: dt.date,
    db: AsyncSession = Depends(get_db_session),
):

    return await AppointmentService(db=db).get_free_intervals(
        doctor_id=doctor_id,
        until=until,
        since=since,
    )
