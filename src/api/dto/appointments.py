import datetime as dt
from uuid import UUID
import typing as t
from pydantic import Field, field_validator, model_validator

from schemas.appointment import ScheduleType, WeekDay
from src.api.dto.base import FrontendModelBase


class CreateAppointmentRule(FrontendModelBase):
    doctor_id: int
    patient_name: str = Field(max_length=100)
    schedule_type: ScheduleType
    date: dt.date
    day_of_week: WeekDay | None
    day_of_month: int | None = Field(default=None, gte=1, lte=31)
    week_number: int | None = Field(default=None, gte=1, lte=4)
    start_at: dt.time
    duration: dt.timedelta

    @field_validator("date")
    def validate_date(
        cls,
        v: dt.date | None,
        *args,
        **kwargs,
    ) -> dt.date | None:
        if v is None:
            return None
        if v + dt.timedelta(days=1) >= dt.date.today():
            return v
        raise ValueError(f"Date must be more than {dt.date.today()}")

    @model_validator(mode="after")
    def check_schedule_type(self) -> t.Any:
        if self.schedule_type == ScheduleType.sole and self.date is None:
            raise ValueError("Date cannot be None for sole appointment.")
        if self.schedule_type == ScheduleType.weekday and self.day_of_week is None:
            raise ValueError("Date cannot be None for weekly appointment.")
        if self.schedule_type == ScheduleType.monthly and self.day_of_month is None:
            raise ValueError("Day of month cannot be None " "for monthly appointment.")
        if (
            self.schedule_type == ScheduleType.monthly_weekday
            and self.day_of_week is None
            or self.week_number is None
        ):
            raise ValueError(
                "day_of_week and week_number cannot be "
                "None for monthly_weekday appointment."
            )


class CreateAppointmentResponse(FrontendModelBase):
    id: UUID
    doctor_id: int
    patient_name: str
    schedule_type: ScheduleType
    date: dt.date
    day_of_week: WeekDay
    day_of_month: int
    week_number: int
    start_at: dt.time
    duration: dt.timedelta
    created_at: dt.datetime
