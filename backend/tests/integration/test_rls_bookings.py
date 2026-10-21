import pytest
from datetime import datetime, timedelta, timezone

pytestmark = pytest.mark.integration


def _seed_booking(supabase_local, patient, doctor_user):
    doctor_row = supabase_local["service"].table("doctors").insert({
        "profile_id": doctor_user["id"],
        "specialty": "Internal Medicine",
        "serves_neighborhoods": ["Mile 16"],
        "contact_method": "phone",
    }).execute().data[0]

    now = datetime.now(timezone.utc)
    booking = supabase_local["service"].table("bookings").insert({
        "doctor_id": doctor_row["id"],
        "patient_id": patient["id"],
        "starts_at": (now + timedelta(days=1)).isoformat(),
        "ends_at": (now + timedelta(days=1, minutes=30)).isoformat(),
        "status": "confirmed",
    }).execute().data[0]

    return booking, doctor_row


def test_patient_cannot_read_other_patients_booking(
    supabase_local, patient_a, patient_b, doctor_user, authed_client
):
    booking, doctor_row = _seed_booking(supabase_local, patient_a, doctor_user)

    client_b = authed_client(patient_b)
    result = client_b.table("bookings").select("*").eq("id", booking["id"]).execute()

    assert result.data == []

    supabase_local["service"].table("bookings").delete().eq("id", booking["id"]).execute()
    supabase_local["service"].table("doctors").delete().eq("id", doctor_row["id"]).execute()


def test_doctor_can_read_own_booking(
    supabase_local, patient_a, doctor_user, authed_client
):
    booking, doctor_row = _seed_booking(supabase_local, patient_a, doctor_user)

    doctor_client = authed_client(doctor_user)
    result = doctor_client.table("bookings").select("*").eq("id", booking["id"]).execute()

    assert len(result.data) == 1

    supabase_local["service"].table("bookings").delete().eq("id", booking["id"]).execute()
    supabase_local["service"].table("doctors").delete().eq("id", doctor_row["id"]).execute()