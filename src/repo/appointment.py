import datetime as dt
from dataclasses import asdict

from sqlalchemy import and_, exists, func, insert, select

from src.db.models import AppointmentRule, ScheduledAppointment
from src.repo.base import RepoBase
from src.schemas.appointment import AppointmentDate, AppointmentInDB


class AppointmentRepo(RepoBase):

    model = AppointmentRule


class ScheduledAppointmentRepo(RepoBase):

    model = ScheduledAppointment

    async def check_intersections_with_for_update(
        self,
        doctor_id: int,
        appointments: list[AppointmentDate],
    ) -> bool:
        conditions = [
            and_(
                self.model.start_at <= appointment.end_at,
                self.model.end_at >= appointment.start_at,
            )
            for appointment in appointments
        ]

        stmt = select(
            exists().where(
                and_(self.model.doctor_id == doctor_id, *conditions),
            )
        ).with_for_update()

        query = await self._db.scalar(stmt)
        return bool(query)

    async def create_many_appointments(
        self,
        appointment: AppointmentInDB,
        appointment_dates: list[AppointmentDate],
    ):
        await self._db.execute(
            insert(self.model),
            [
                {
                    **asdict(dates),
                    "appointment_rule_id": appointment.id,
                    "doctor_id": appointment.doctor_id,
                }
                for dates in appointment_dates
            ],
        )

    @staticmethod
    def __convert_to_datetime(datetime: str) -> dt.datetime:
        datetime = dt.datetime.strptime(datetime, "%Y-%m-%dT%H:%M:%S.%f")
        return datetime.replace(tzinfo=dt.timezone.utc)

    def __convert_events_to_datetime(self, events):
        for _, event_data in events.items():
            event_data["start_at"] = self.__convert_to_datetime(
                datetime=event_data["start_at"],
            )
            event_data["end_at"] = self.__convert_to_datetime(
                datetime=event_data["end_at"],
            )
        return events

    async def get_free_intervals(
        self,
        doctor_id: int,
        since: dt.date,
        until: dt.date,
    ):
        stmt = (
            select(
                func.date(self.model.start_at).label("event_date"),
                self.model.start_at,
                self.model.end_at,
            )
            .where(
                self.model.doctor_id == doctor_id,
                (self.model.start_at > since) | (self.model.end_at < until),
            )
            .order_by(self.model.start_at)
        )

        results = await self._db.execute(stmt)

        grouped_events = {}
        for row in results.mappings().all():
            event_date = row.event_date
            if event_date not in grouped_events:
                grouped_events[event_date] = []
            start_at: dt.datetime = row.start_at
            end_at: dt.datetime = row.end_at
            grouped_events[event_date].append(
                {
                    "start_at": start_at.replace(tzinfo=dt.timezone.utc),
                    "end_at": end_at.replace(tzinfo=dt.timezone.utc),
                }
            )
        return grouped_events
