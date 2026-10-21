import pytest

pytestmark = pytest.mark.integration


def test_doctor_owns_their_row(supabase_local, doctor_user, authed_client):
    client = authed_client(doctor_user)

    created = client.table("doctors").insert({
        "profile_id": doctor_user["id"],
        "specialty": "Cardiology",
        "serves_neighborhoods": ["Bokova"],
        "contact_method": "phone",
    }).execute()

    assert len(created.data) == 1
    assert created.data[0]["profile_id"] == doctor_user["id"]

    updated = client.table("doctors").update({"bio": "Cardio in Bokova"}) \
        .eq("id", created.data[0]["id"]).execute()
    assert updated.data[0]["bio"] == "Cardio in Bokova"

    # cleanup
    supabase_local["service"].table("doctors").delete() \
        .eq("id", created.data[0]["id"]).execute()


def test_hospital_admin_cannot_edit_doctor(
    supabase_local, doctor_user, hospital_admin_user, authed_client
):
    # doctor creates own row via service role (simpler; ownership already tested above)
    created = supabase_local["service"].table("doctors").insert({
        "profile_id": doctor_user["id"],
        "specialty": "Pediatrics",
        "serves_neighborhoods": ["Molyko"],
        "contact_method": "phone",
    }).execute().data[0]

    admin_client = authed_client(hospital_admin_user)
    result = admin_client.table("doctors").update({"bio": "hijacked"}) \
        .eq("id", created["id"]).execute()

    # RLS silently filters the row — 0 updated
    assert result.data == []

    # verify unchanged
    row = supabase_local["service"].table("doctors").select("bio") \
        .eq("id", created["id"]).maybe_single().execute()
    assert row.data["bio"] is None

    supabase_local["service"].table("doctors").delete() \
        .eq("id", created["id"]).execute()


def test_doctor_cannot_edit_another_doctor(
    supabase_local, doctor_user, authed_client
):
    from tests.integration.conftest import _create_user
    other = _create_user(supabase_local, "doctor", "Other Doctor")

    created = supabase_local["service"].table("doctors").insert({
        "profile_id": doctor_user["id"],
        "specialty": "Dermatology",
        "serves_neighborhoods": ["Bomaka"],
        "contact_method": "phone",
    }).execute().data[0]

    other_client = authed_client(other)
    result = other_client.table("doctors").update({"bio": "hijacked"}) \
        .eq("id", created["id"]).execute()

    assert result.data == []

    supabase_local["service"].table("doctors").delete() \
        .eq("id", created["id"]).execute()
    supabase_local["service"].auth.admin.delete_user(other["id"])