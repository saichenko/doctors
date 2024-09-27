import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import Response

from exceptions import (
    DoctorSessionDurationExceededError,
    NotFoundError,
    SelectedDateIsExceededError,
    SelectedScheduleIsNotAvailableError,
)
from src.api.core import main_router
from src.core.config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(main_router)


@app.exception_handler(NotFoundError)
async def handle_not_found(*args, **kwargs) -> Response:
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(SelectedScheduleIsNotAvailableError)
async def handle_availability_exception(*args, **kwargs) -> Response:
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(DoctorSessionDurationExceededError)
async def handle_session_duration_exception(*args, **kwargs) -> Response:
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(SelectedDateIsExceededError)
async def handle_dates_exception(*args, **kwargs) -> Response:
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )
