import uuid
from datetime import datetime, time, timedelta

from sqlalchemy import Date, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.schemas.appointment import AppointmentInDB, ScheduleType
from src.schemas.doctors import DoctorInDB

UTC_DATETIME_NOW = text("TIMEZONE ('utc', now())")


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100))
    summary: Mapped[str] = mapped_column(
        String(length=300),
        nullable=True,
    )
    max_session_duration: Mapped[timedelta]
    available_time_start: Mapped[time]
    available_time_end: Mapped[time]
    created_at: Mapped[datetime] = mapped_column(
        server_default=UTC_DATETIME_NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=UTC_DATETIME_NOW,
        onupdate=True,
    )

    def to_dataclass(self) -> DoctorInDB:
        return DoctorInDB(
            id=self.id,
            name=self.name,
            summary=self.summary,
            max_session_duration=self.max_session_duration,
            available_time_start=self.available_time_start,
            available_time_end=self.available_time_end,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ScheduledAppointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    appointment_rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("appointment_rules.id"),
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        index=True,
    )
    start_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime] = mapped_column()


class AppointmentRule(Base):
    __tablename__ = "appointment_rules"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    doctor_id: Mapped[UUID] = mapped_column(
        ForeignKey("doctors.id"),
        index=True,
    )
    patient_name: Mapped[str] = mapped_column(String(length=100))

    schedule_type: Mapped[ScheduleType]
    date: Mapped[datetime.date] = mapped_column(
        Date
    )  # Can be used as start date or sole.
    day_of_week: Mapped[int] = mapped_column(nullable=True)
    day_of_month: Mapped[int] = mapped_column(nullable=True)
    week_number: Mapped[int] = mapped_column(nullable=True)

    start_at: Mapped[time]
    duration: Mapped[timedelta]

    created_at: Mapped[datetime] = mapped_column(
        server_default=UTC_DATETIME_NOW,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=UTC_DATETIME_NOW,
        onupdate=True,
    )

    def to_dataclass(self) -> AppointmentInDB:
        return AppointmentInDB(
            id=self.id,
            doctor_id=self.doctor_id,
            patient_name=self.patient_name,
            schedule_type=self.schedule_type,
            date=self.date,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            week_number=self.week_number,
            start_at=self.start_at,
            duration=self.duration,
            created_at=self.created_at,
        )
