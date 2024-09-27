import datetime as dt

from pydantic import Field

from src.api.dto.base import FrontendModelBase


class DoctorModelBase(FrontendModelBase):
    name: str = Field(max_length=100)
    summary: str | None = Field(default=None, max_length=100)
    max_session_duration: dt.timedelta | None = None


class CreateDoctorRequest(DoctorModelBase):
    available_time_start: dt.time
    available_time_end: dt.time


class DoctorDetailsResponse(DoctorModelBase):
    id: int
    created_at: dt.datetime
