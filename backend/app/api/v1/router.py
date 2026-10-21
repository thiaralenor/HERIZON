from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.doctors.router import router as doctors_router
from app.modules.freelancers.router import router as freelancers_router
from app.modules.hospitals.router import router as hospitals_router
from app.modules.patients.router import router as patients_router
from app.modules.sos.router import router as sos_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(doctors_router)
api_router.include_router(freelancers_router)
api_router.include_router(patients_router)
api_router.include_router(hospitals_router)
api_router.include_router(sos_router)
