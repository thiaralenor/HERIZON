from uuid import UUID

from app.db.supabase_client import get_service_client


def fetch_profile(user_id: str) -> dict | None:
    db = get_service_client()
    res = db.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    return res.data if res else None


def fetch_doctor_link(user_id: str) -> dict | None:
    """Returns the doctors row for this user, if any (hospital or freelance)."""
    db = get_service_client()
    res = (
        db.table("doctors")
        .select("id, hospital_id, doctor_type")
        .eq("profile_id", user_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None


def fetch_admin_hospital(user_id: str) -> dict | None:
    """Returns the hospital this user administers, if any."""
    db = get_service_client()
    res = (
        db.table("hospitals")
        .select("id, name")
        .eq("created_by", user_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None