import pytest
from datetime import datetime, timedelta, timezone
from app.modules.bookings import service as booking_service


def test_double_booking_rejected(db, doctor, patient):
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(minutes=30)

    booking_service.create_booking(
        {"doctor_id": doctor["id"], "starts_at": start, "ends_at": end}, patient["id"]
    )

    with pytest.raises(booking_service.SlotTakenError):
        booking_service.create_booking(
            {"doctor_id": doctor["id"], "starts_at": start, "ends_at": end},
            patient["id"],
        )


def test_cancelled_booking_releases_slot(db, doctor, patient):
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(minutes=30)
    b = booking_service.create_booking(
        {"doctor_id": doctor["id"], "starts_at": start, "ends_at": end}, patient["id"]
    )
    booking_service.update_status(b["id"], "cancelled")
    # Should succeed now
    booking_service.create_booking(
        {"doctor_id": doctor["id"], "starts_at": start, "ends_at": end}, patient["id"]
    )