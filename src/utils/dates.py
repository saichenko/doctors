import datetime as dt
import typing as t


def iterate_between_dates(
    start_date: dt.date,
    end_date: dt.date,
) -> t.Iterator[dt.date]:
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += dt.timedelta(days=1)
