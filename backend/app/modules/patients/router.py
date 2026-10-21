from fastapi import APIRouter, HTTPException

from app.modules.patients.schemas import BookingCreate, BookingOptions, BookingReceipt
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
