from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.patients import service
from app.modules.patients.schemas import (
    BookingCreate,
    BookingOptions,
    BookingReceipt,
    SymptomLogCreate,
    SymptomLogOut,
)
from app.modules.patients.service import create_booking, get_booking_options

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/booking-options", response_model=BookingOptions)
def booking_options() -> BookingOptions:
	return get_booking_options()


@router.post("/bookings", response_model=BookingReceipt, status_code=201)
def request_booking(request: BookingCreate) -> BookingReceipt:
	try:
		return create_booking(request)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error)) from error

@router.post(
    "/me/symptoms",
    response_model=SymptomLogOut,
    status_code=status.HTTP_201_CREATED,
)
def log_symptom(
    payload: SymptomLogCreate,
    user: CurrentUser = Depends(require_role("patient")),
):
    return service.create_log(user.id, payload.model_dump(exclude_none=True))


@router.get("/me/symptoms", response_model=list[SymptomLogOut])
def my_symptoms(
    user: CurrentUser = Depends(require_role("patient")),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_logs(user.id, limit, offset)


@router.delete("/me/symptoms/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_symptom(
    log_id: str,
    user: CurrentUser = Depends(require_role("patient")),
):
    if not service.delete_log(user.id, log_id):
        raise HTTPException(status_code=404, detail="Log not found")
