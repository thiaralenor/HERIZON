import pytest

pytestmark = pytest.mark.integration


def test_symptom_log_is_private(supabase_local, patient_a, patient_b, authed_client):
    log = supabase_local["service"].table("symptom_logs").insert({
        "patient_id": patient_a["id"],
        "symptoms": "headache",
        "severity": 6,
    }).execute().data[0]

    client_b = authed_client(patient_b)
    result = client_b.table("symptom_logs").select("*").eq("id", log["id"]).execute()
    assert result.data == []

    supabase_local["service"].table("symptom_logs").delete().eq("id", log["id"]).execute()