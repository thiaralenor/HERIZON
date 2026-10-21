from datetime import date, timedelta
from uuid import uuid4

from app.modules.patients.schemas import (
	BookingCreate,
	BookingOptions,
	BookingReceipt,
	HospitalOption,
	ProviderOption,
)

HOSPITALS = [
	HospitalOption(id="north-clinic", name="Northside Medical Centre", location="Central District"),
	HospitalOption(id="river-hospital", name="Riverside General Hospital", location="River District"),
]

PROVIDERS = [
	ProviderOption(
		id="dr-amara-okafor",
		name="Dr. Amara Okafor",
		specialty="General Practice",
		hospital_id="north-clinic",
		next_available=date.today() + timedelta(days=1),
	),
	ProviderOption(
		id="dr-leo-mensah",
		name="Dr. Leo Mensah",
		specialty="Cardiology",
		hospital_id="north-clinic",
		next_available=date.today() + timedelta(days=2),
	),
	ProviderOption(
		id="dr-nia-adebayo",
		name="Dr. Nia Adebayo",
		specialty="Paediatrics",
		hospital_id="river-hospital",
		next_available=date.today() + timedelta(days=1),
	),
	ProviderOption(
		id="dr-samira-bello",
		name="Dr. Samira Bello",
		specialty="General Practice",
		next_available=date.today() + timedelta(days=1),
	),
	ProviderOption(
		id="dr-kofi-boateng",
		name="Dr. Kofi Boateng",
		specialty="Dermatology",
		next_available=date.today() + timedelta(days=3),
	),
]

_booking_requests: list[BookingReceipt] = []


def get_booking_options() -> BookingOptions:
	return BookingOptions(
		hospitals=HOSPITALS,
		providers=PROVIDERS,
		specialties=sorted({provider.specialty for provider in PROVIDERS}),
	)


def create_booking(request: BookingCreate) -> BookingReceipt:
	if request.appointment_date < date.today():
		raise ValueError("Appointment date must be today or later.")

	provider = next((item for item in PROVIDERS if item.id == request.doctor_id), None)
	if provider is None:
		raise ValueError("Selected provider was not found.")

	if request.provider_type == "hospital":
		if request.hospital_id is None:
			raise ValueError("Choose a hospital for hospital-employed doctors.")
		if provider.hospital_id != request.hospital_id:
			raise ValueError("This doctor is not affiliated with the selected hospital.")
		hospital = next(item for item in HOSPITALS if item.id == request.hospital_id)
		hospital_name = hospital.name
	else:
		if request.hospital_id is not None or provider.hospital_id is not None:
			raise ValueError("Freelance bookings must use an independent provider.")
		hospital_name = None

	receipt = BookingReceipt(
		id=str(uuid4()),
		provider_name=provider.name,
		provider_type=request.provider_type,
		hospital_name=hospital_name,
		appointment_date=request.appointment_date,
		appointment_time=request.appointment_time,
	)
	_booking_requests.append(receipt)
	return receipt

from app.db.supabase_client import get_service_client


def create_log(patient_id: str, payload: dict) -> dict:
    db = get_service_client()
    row = {**payload, "patient_id": patient_id}
    return db.table("symptom_logs").insert(row).execute().data[0]


def list_logs(
    patient_id: str, limit: int = 50, offset: int = 0
) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("symptom_logs")
        .select("*")
        .eq("patient_id", patient_id)
        .order("logged_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return res.data or []


def get_log(patient_id: str, log_id: str) -> dict | None:
    db = get_service_client()
    res = (
        db.table("symptom_logs")
        .select("*")
        .eq("id", log_id)
        .eq("patient_id", patient_id)     # defense-in-depth; RLS also enforces
        .maybe_single()
        .execute()
    )
    return res.data if res else None


def delete_log(patient_id: str, log_id: str) -> bool:
    db = get_service_client()
    res = (
        db.table("symptom_logs")
        .delete()
        .eq("id", log_id)
        .eq("patient_id", patient_id)
        .execute()
    )
    return bool(res.data)
