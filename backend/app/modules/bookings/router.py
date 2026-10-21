from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.bookings import service
from app.modules.bookings.schemas import BookingCreate, BookingOut, BookingStatusUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    user: CurrentUser = Depends(require_role("patient")),
):
    try:
        return service.create_booking(payload.model_dump(), user.id)
    except service.SlotTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That slot was just taken. Please pick another.",
        )


@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    user: CurrentUser = Depends(require_role("patient")),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_for_patient(user.id, limit, offset)


@router.get("/doctor/me", response_model=list[BookingOut])
def my_doctor_bookings(
    user: CurrentUser = Depends(require_role("doctor", "freelancer")),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    # Look up the doctor row for this user
    from app.modules.doctors.service import get_doctor_by_profile

    doctor = get_doctor_by_profile(user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return service.list_for_doctor(doctor["id"], limit, offset)


@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: str,
    payload: BookingStatusUpdate,
    user: CurrentUser = Depends(require_role("patient", "doctor", "freelancer")),
):
    booking = service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Patients may only cancel their own booking
    if user.role == "patient":
        if booking["patient_id"] != user.id:
            raise HTTPException(status_code=403, detail="Not your booking")
        if payload.status != "cancelled":
            raise HTTPException(
                status_code=403, detail="Patients can only cancel bookings"
            )
    else:
        # Doctors may mark their own bookings completed / no_show / cancelled
        from app.modules.doctors.service import get_doctor_by_profile

        doctor = get_doctor_by_profile(user.id)
        if not doctor or booking["doctor_id"] != doctor["id"]:
            raise HTTPException(status_code=403, detail="Not your booking")

    return service.update_status(booking_id, payload.status)
