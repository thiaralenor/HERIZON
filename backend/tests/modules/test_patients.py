from datetime import date, timedelta

import pytest

from app.modules.patients.schemas import BookingCreate
from app.modules.patients.service import create_booking


def make_request(
    doctor_id: str,
    provider_type: str = "hospital",
    hospital_id: str | None = "north-clinic",
) -> BookingCreate:
    return BookingCreate(
        patient_name="Taylor Patient",
        patient_email="taylor@example.com",
        provider_type=provider_type,
        hospital_id=hospital_id,
        doctor_id=doctor_id,
        appointment_date=date.today() + timedelta(days=2),
        appointment_time="10:30",
    )


def test_hospital_booking_keeps_selected_hospital() -> None:
    receipt = create_booking(make_request("dr-amara-okafor"))

    assert receipt.provider_type == "hospital"
    assert receipt.hospital_name == "Northside Medical Centre"


def test_hospital_booking_rejects_doctor_from_another_hospital() -> None:
    with pytest.raises(ValueError, match="not affiliated"):
        create_booking(make_request("dr-nia-adebayo", hospital_id="north-clinic"))


def test_freelance_booking_rejects_hospital_employed_doctor() -> None:
    with pytest.raises(ValueError, match="independent provider"):
        create_booking(make_request("dr-amara-okafor", provider_type="freelance", hospital_id=None))


def test_freelance_booking_has_no_hospital() -> None:
    receipt = create_booking(make_request("dr-samira-bello", provider_type="freelance", hospital_id=None))

    assert receipt.provider_type == "freelance"
    assert receipt.hospital_name is None
