import datetime as dt
from dataclasses import dataclass


@dataclass
class DoctorInDB:
    id: int
    name: str
    summary: str | None
    max_session_duration: dt.timedelta | None
    available_time_start: dt.time
    available_time_end: dt.time
    created_at: dt.datetime
    updated_at: dt.datetime


@dataclass
class CreateDoctor:
    name: str
    summary: str | None
    max_session_duration: dt.timedelta | None
    available_time_start: dt.time
    available_time_end: dt.time
