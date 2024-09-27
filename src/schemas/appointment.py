import dataclasses
import datetime as dt
import enum
import typing as t
from uuid import UUID


class WeekDay(enum.IntEnum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class ScheduleType(str, enum.Enum):
    sole = "sole"
    weekday = "weekday"
    monthly = "monthly"
    monthly_weekday = "monthly_weekday"


@dataclasses.dataclass
class CreateAppointment:
    doctor_id: int
    patient_name: str
    schedule_type: ScheduleType
    date: dt.date
    day_of_week: WeekDay | None
    day_of_month: int | None
    week_number: int | None
    start_at: dt.time
    duration: dt.timedelta


@dataclasses.dataclass
class AppointmentDate:
    start_at: dt.datetime
    end_at: dt.datetime


@dataclasses.dataclass
class AppointmentInDB:
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


class Interval(t.TypedDict):
    start_at: dt.datetime
    end_at: dt.datetime
