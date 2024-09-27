import calendar
import datetime as dt
import typing as t
from collections import defaultdict

from exceptions import (
    DoctorNotFoundError,
    DoctorSessionDurationExceededError,
    SelectedDateIsExceededError,
    SelectedScheduleIsNotAvailableError,
)
from schemas.appointment import CreateAppointment, Interval
from service.base import ServiceBase
from src.core.config import settings
from src.repo.appointment import AppointmentRepo, ScheduledAppointmentRepo
from src.repo.doctors import DoctorRepo
from src.schemas.appointment import AppointmentDate, AppointmentInDB, ScheduleType
from src.schemas.doctors import DoctorInDB
from utils.dates import iterate_between_dates


class AppointmentService(ServiceBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doctor_repo = DoctorRepo(db=self._db)
        self.__appointment_repo = AppointmentRepo(db=self._db)
        self.__schedule_appointment_repo = ScheduledAppointmentRepo(
            db=self._db,
        )

        self.__schedule_for_days = settings.SCHEDULE_FOR_DAYS
        self.__schedule_until = (
            dt.datetime.utcnow() + dt.timedelta(days=self.__schedule_for_days)
        ).replace(tzinfo=dt.timezone.utc)

    async def __save_appointment(
        self,
        appointment: CreateAppointment,
        appointments: t.List[AppointmentDate],
    ) -> AppointmentInDB:
        created = await self.__appointment_repo.create(data=appointment)
        await self.__schedule_appointment_repo.create_many_appointments(
            appointment_dates=appointments,
            appointment=created,
        )
        return created

    async def __is_schedule_free(
        self,
        doctor_id: int,
        appointments: t.List[AppointmentDate],
    ) -> bool:
        is_found = (
            await self.__schedule_appointment_repo.check_intersections_with_for_update(
                doctor_id=doctor_id,
                appointments=appointments,
            )
        )
        return not is_found

    def __check_date_excess(
        self,
        value: dt.datetime,
        raise_exception: bool = False,
    ) -> bool:
        is_exceeded = value > self.__schedule_until
        if raise_exception is True and is_exceeded is True:
            raise SelectedDateIsExceededError
        return is_exceeded

    async def __check_if_available(
        self,
        doctor: DoctorInDB,
        data: CreateAppointment,
    ):
        if doctor.max_session_duration < data.duration:
            raise DoctorSessionDurationExceededError

    async def __calculate_sole(
        self,
        data: CreateAppointment,
    ) -> list[AppointmentDate]:
        start_at = dt.datetime.combine(data.date, data.start_at)
        end_at = start_at + data.duration
        return [AppointmentDate(start_at=start_at, end_at=end_at)]

    async def __calculate_weekday(
        self,
        data: CreateAppointment,
    ) -> list[AppointmentDate]:
        appointments: list[AppointmentDate] = []
        start_at = dt.datetime.combine(data.date, data.start_at)
        end_at = start_at + data.duration
        while self.__check_date_excess(end_at) is False:
            appointments.append(
                AppointmentDate(
                    start_at=start_at,
                    end_at=end_at,
                )
            )
            start_at = start_at + dt.timedelta(weeks=1)
            end_at = start_at + data.duration
        return appointments

    async def __calculate_monthly(
        self,
        data: CreateAppointment,
    ) -> list[AppointmentDate]:
        nearest = data.date
        _, nearset_month_days = calendar.monthrange(
            year=nearest.year,
            month=nearest.month,
        )
        if nearest.day > data.day_of_month:
            nearest = nearest.replace(
                month=nearest.month + 1,
                day=data.day_of_month,
            )
        elif nearest.day < data.day_of_month:
            if nearset_month_days < data.day_of_month:
                day = nearset_month_days
            else:
                day = data.day_of_month
            nearest = nearest.replace(
                day=day,
            )

        start_at = dt.datetime.combine(nearest, data.start_at)
        last: AppointmentDate = AppointmentDate(
            start_at=start_at,
            end_at=start_at + data.duration,
        )
        self.__check_date_excess(last.end_at, raise_exception=True)
        appointments: list[AppointmentDate] = [
            last,
        ]

        while self.__check_date_excess(last.end_at) is False:
            last_year = last.start_at.year
            last_month = last.start_at.month
            day = data.day_of_month
            year = last_year + 1 if last_month == 12 else last_year
            month = 1 if last_month == 12 else last_month + 1

            _, month_days = calendar.monthrange(
                year=year,
                month=month,
            )
            if day > month_days:
                day = month_days  # Set last day of month.
            delta_appointment = last.start_at.replace(
                year=year,
                month=month,
                day=day,
            )
            appointment = AppointmentDate(
                start_at=delta_appointment,
                end_at=delta_appointment + data.duration,
            )
            appointments.append(appointment)
            last = appointment
        return appointments

    async def __calculate_monthly_weekday(
        self,
        data: CreateAppointment,
    ) -> list[AppointmentDate]:
        start_date = dt.datetime.combine(data.date, data.start_at)
        delta_date = start_date
        appointments: list[AppointmentDate] = []
        while self.__check_date_excess(delta_date) is False:
            _, month_days = calendar.monthrange(
                year=delta_date.year,
                month=delta_date.month,
            )
            occurrences = 0
            for day in range(1, month_days):
                delta_date = delta_date.replace(day=day)

                weekday = calendar.weekday(
                    year=delta_date.year,
                    month=delta_date.month,
                    day=delta_date.day,
                )
                if weekday == data.day_of_week:
                    occurrences += 1
                if occurrences == data.week_number:
                    if delta_date.date() < data.date:
                        continue
                    appointment = AppointmentDate(
                        start_at=delta_date,
                        end_at=delta_date + data.duration,
                    )
                    appointments.append(appointment)
                    break
            month = 1 if delta_date.month == 12 else delta_date.month + 1
            year = delta_date.year + 1 if delta_date.month == 12 else delta_date.year
            delta_date = delta_date.replace(
                year=year,
                month=month,
                day=1,
            )
        return appointments

    async def __calculate_next_appointments(
        self,
        data: CreateAppointment,
    ) -> list[AppointmentDate]:
        date_as_datetime = dt.datetime.combine(
            date=data.date,
            time=dt.datetime.min.time(),
            tzinfo=dt.timezone.utc,
        )
        self.__check_date_excess(date_as_datetime, raise_exception=True)
        match data.schedule_type:
            case ScheduleType.sole:
                return await self.__calculate_sole(data)
            case ScheduleType.weekday:
                return await self.__calculate_weekday(data)
            case ScheduleType.monthly:
                return await self.__calculate_monthly(data)
            case ScheduleType.monthly_weekday:
                return await self.__calculate_monthly_weekday(data)
            case _ as unreachable:
                t.assert_never(unreachable)

    async def create_appointment(
        self,
        data: CreateAppointment,
    ) -> AppointmentInDB:
        doctor = await self.__doctor_repo.get_by_id(data.doctor_id)
        if doctor is None:
            raise DoctorNotFoundError
        dates = await self.__calculate_next_appointments(data)
        can_schedule = await self.__is_schedule_free(
            appointments=dates,
            doctor_id=data.doctor_id,
        )
        if can_schedule is False:
            raise SelectedScheduleIsNotAvailableError
        return await self.__save_appointment(data, dates)

    @staticmethod
    def __calculate_slots(
        date: dt.date,
        available_start_at: dt.time,
        available_end_at: dt.time,
        scheduled: list[dict],
    ) -> list[Interval]:
        scheduled: list[Interval] = sorted(
            scheduled,
            key=lambda x: x["start_at"],
        )
        slots = []
        delta = dt.datetime.combine(
            date=date,
            time=available_start_at,
            tzinfo=dt.timezone.utc,
        )
        if available_end_at <= available_start_at:
            # In case of next day in UTC timezone.
            end_at = (delta + dt.timedelta(days=1)).replace(
                hour=available_end_at.hour,
                minute=available_end_at.minute,
                second=available_end_at.second,
            )
        else:
            end_at = delta.replace(
                hour=available_end_at.hour,
                minute=available_end_at.minute,
                second=available_end_at.second,
            )

        while delta < end_at:
            delta_start: dt.datetime = delta
            delta_end = delta = delta_start + dt.timedelta(minutes=15)
            delta_scheduled = None
            if scheduled:
                delta_scheduled = scheduled[0]
            if delta_scheduled is not None:
                start_at = delta_scheduled["start_at"]
                end_at = delta_scheduled["end_at"]
                if (
                    (end_at > delta_end > start_at)
                    or (delta_end == end_at == start_at)
                    or (start_at < delta_start < end_at)
                ):
                    continue

                if delta_start >= end_at:
                    scheduled.pop(0)
            interval: Interval = {"start_at": delta_start, "end_at": delta_end}
            slots.append(interval)
        return slots

    async def __split_ranges_by_intervals(
        self,
        since: dt.date,
        until: dt.date,
        doctor: DoctorInDB,
        appointments,
    ):
        appointments = defaultdict(list, appointments)
        intervals: dict[dt.date, list[Interval]] = {}
        for date in iterate_between_dates(since, until):
            intervals[date] = self.__calculate_slots(
                date=date,
                available_start_at=doctor.available_time_start,
                available_end_at=doctor.available_time_end,
                scheduled=appointments[date],
            )
        return intervals

    async def get_free_intervals(
        self,
        doctor_id: int,
        since: dt.date,
        until: dt.date,
    ):
        until = min(until, self.__schedule_until.date())
        since = max(since, dt.datetime.now(tz=dt.timezone.utc).date())
        doctor = await self.__doctor_repo.get_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundError
        data = await self.__schedule_appointment_repo.get_free_intervals(
            doctor_id=doctor_id,
            until=until,
            since=since,
        )
        intervals = await self.__split_ranges_by_intervals(
            doctor=doctor, appointments=data, since=since, until=until
        )
        return intervals
