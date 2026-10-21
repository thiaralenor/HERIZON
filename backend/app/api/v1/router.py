from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.doctors.router import router as doctors_router
from app.modules.hospitals.router import router as hospitals_router
from app.modules.bookings.router import router as bookings_router
from app.modules.patients.router import router as patients_router
from app.modules.dispatch.router import router as dispatch_router
from app.modules.emergency.router import router as emergency_router
from app.modules.notifications.router import router as notifications_router






api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(hospitals_router)
api_router.include_router(doctors_router)
api_router.include_router(bookings_router)
api_router.include_router(patients_router)
api_router.include_router(emergency_router)
api_router.include_router(dispatch_router)
api_router.include_router(notifications_router)