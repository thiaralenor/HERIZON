from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.doctors import service
from app.modules.doctors.schemas import DoctorCreate, DoctorOut, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorOut])
def list_doctors(
    doctor_type: str | None = Query(None, pattern="^(hospital|freelance)$"),
    hospital_id: str | None = Query(None),
    specialty: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_doctors(
        doctor_type=doctor_type,
        hospital_id=hospital_id,
        specialty=specialty,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/by-slug/{slug}", response_model=DoctorOut)
def get_doctor_by_slug(slug: str):
    d = service.get_doctor_by_slug(slug)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: str):
    d = service.get_doctor_by_id(doctor_id)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(
    payload: DoctorCreate,
    user: CurrentUser = Depends(require_role("doctor", "freelancer")),
):
    # Role ↔ doctor_type must match
    if user.role == "freelancer" and payload.doctor_type != "freelance":
        raise HTTPException(status_code=400, detail="Freelancer must use doctor_type=freelance")
    if user.role == "doctor" and payload.doctor_type != "hospital":
        raise HTTPException(status_code=400, detail="Hospital doctor must use doctor_type=hospital")

    # One doctor row per profile
    if service.get_doctor_by_profile(user.id):
        raise HTTPException(status_code=409, detail="Doctor profile already exists")

    return service.create_doctor(payload.model_dump(exclude_none=True), user.id)


@router.patch("/me", response_model=DoctorOut)
def update_my_doctor(
    payload: DoctorUpdate,
    user: CurrentUser = Depends(require_role("doctor", "freelancer")),
):
    me = service.get_doctor_by_profile(user.id)
    if not me:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return service.update_doctor(me["id"], payload.model_dump(exclude_none=True))

from datetime import date
from app.modules.doctors import availability_service
from app.modules.doctors.availability_schemas import (
    AvailabilityIn,
    AvailabilityOut,
    SlotOut,
    SlotsResponse,
    TimeOffIn,
    TimeOffOut,
)


def _assert_own_doctor(user: CurrentUser) -> dict:
    me = service.get_doctor_by_profile(user.id)
    if not me:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return me


@router.get("/me/availability", response_model=list[AvailabilityOut])
def get_my_availability(user: CurrentUser = Depends(require_role("doctor", "freelancer"))):
    me = _assert_own_doctor(user)
    return availability_service.list_availability(me["id"])


@router.put("/me/availability", response_model=list[AvailabilityOut])
def set_my_availability(
    rules: list[AvailabilityIn],
    user: CurrentUser = Depends(require_role("doctor", "freelancer")),
):
    me = _assert_own_doctor(user)
    return availability_service.replace_availability(
        me["id"], [r.model_dump() for r in rules]
    )


@router.get("/me/time-off", response_model=list[TimeOffOut])
def list_my_time_off(user: CurrentUser = Depends(require_role("doctor", "freelancer"))):
    me = _assert_own_doctor(user)
    return availability_service.list_time_off(me["id"])


@router.post(
    "/me/time-off", response_model=TimeOffOut, status_code=status.HTTP_201_CREATED
)
def add_my_time_off(
    payload: TimeOffIn,
    user: CurrentUser = Depends(require_role("doctor", "freelancer")),
):
    me = _assert_own_doctor(user)
    return availability_service.add_time_off(
        me["id"], payload.model_dump(mode="json")
    )


@router.get("/{doctor_id}/availability", response_model=list[AvailabilityOut])
def get_doctor_availability(doctor_id: str):
    if not service.get_doctor_by_id(doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    return availability_service.list_availability(doctor_id)


@router.get("/{doctor_id}/slots", response_model=SlotsResponse)
def get_doctor_slots(
    doctor_id: str,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    tz: str = Query("Africa/Douala"),
):
    if not service.get_doctor_by_id(doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    try:
        return availability_service.generate_slots(doctor_id, from_date, to_date, tz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))