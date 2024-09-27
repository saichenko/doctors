from fastapi import APIRouter

from src.api.routes.appointments import router as appointments_router
from src.api.routes.doctors import router as doctors_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(doctors_router)
main_router.include_router(appointments_router)
