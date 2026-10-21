from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from postgrest.exceptions import APIError

from app.modules.bookings import service


def _api_error(code: str) -> APIError:
    err = APIError({"message": "x", "code": code})
    return err


def test_create_booking_maps_exclusion_violation_to_slot_taken(mock_supabase_db):
    mock_supabase_db.table.return_value.insert.return_value.execute.side_effect = (
        _api_error("23P01")
    )

    payload = {
        "doctor_id": "doc-1",
        "starts_at": datetime.now(timezone.utc),
        "ends_at": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    with patch("app.modules.bookings.service.get_service_client", return_value=mock_supabase_db):
        with pytest.raises(service.SlotTakenError):
            service.create_booking(payload, "pat-1")


def test_create_booking_re_raises_other_api_errors(mock_supabase_db):
    mock_supabase_db.table.return_value.insert.return_value.execute.side_effect = (
        _api_error("23503")  # foreign key violation
    )

    payload = {
        "doctor_id": "missing-doctor",
        "starts_at": datetime.now(timezone.utc),
        "ends_at": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    with patch("app.modules.bookings.service.get_service_client", return_value=mock_supabase_db):
        with pytest.raises(APIError) as exc:
            service.create_booking(payload, "pat-1")

    assert exc.value.code == "23503"


def test_create_booking_auto_confirms(mock_supabase_db):
    inserted = {"id": "b-1", "status": "confirmed"}
    mock_supabase_db.table.return_value.insert.return_value.execute.return_value.data = [inserted]
    mock_supabase_db.table.return_value.select.return_value.eq.return_value \
        .maybe_single.return_value.execute.return_value.data = {
            "id": "b-1",
            "status": "confirmed",
            "doctor_id": "doc-1",
            "patient_id": "pat-1",
            "starts_at": "2026-10-21T10:00:00+00:00",
            "ends_at": "2026-10-21T10:30:00+00:00",
            "reason": None,
            "created_at": "2026-10-20T10:00:00+00:00",
            "doctors": None,
            "profiles": None,
        }

    payload = {
        "doctor_id": "doc-1",
        "starts_at": datetime.now(timezone.utc),
        "ends_at": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    with patch("app.modules.bookings.service.get_service_client", return_value=mock_supabase_db):
        result = service.create_booking(payload, "pat-1")

    assert result["status"] == "confirmed"