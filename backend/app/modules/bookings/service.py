from postgrest.exceptions import APIError

from app.db.supabase_client import get_service_client

_SELECT = (
    "id, doctor_id, patient_id, starts_at, ends_at, status, reason, created_at, "
    "doctors:doctor_id(slug, profiles:profile_id(full_name)), "
    "profiles:patient_id(full_name)"
)


def _flatten(row: dict) -> dict:
    doctor = row.pop("doctors", None) or {}
    doctor_profile = doctor.get("profiles") or {}
    patient_profile = row.pop("profiles", None) or {}
    row["doctor_name"] = doctor_profile.get("full_name")
    row["doctor_slug"] = doctor.get("slug")
    row["patient_name"] = patient_profile.get("full_name")
    return row


class SlotTakenError(Exception):
    pass


def create_booking(payload: dict, patient_id: str) -> dict:
    db = get_service_client()
    row = {
        "doctor_id": payload["doctor_id"],
        "patient_id": patient_id,
        "starts_at": payload["starts_at"].isoformat(),
        "ends_at": payload["ends_at"].isoformat(),
        "status": "confirmed",            # auto-confirm
        "reason": payload.get("reason"),
    }
    try:
        created = db.table("bookings").insert(row).execute().data[0]
    except APIError as e:
        # 23P01 = exclusion_violation, triggered by no_overlapping_bookings
        if e.code == "23P01":
            raise SlotTakenError() from e
        raise
    return get_booking(created["id"])


def get_booking(booking_id: str) -> dict | None:
    db = get_service_client()
    res = db.table("bookings").select(_SELECT).eq("id", booking_id).maybe_single().execute()
    return _flatten(res.data) if res and res.data else None


def list_for_patient(patient_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("bookings")
        .select(_SELECT)
        .eq("patient_id", patient_id)
        .order("starts_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return [_flatten(r) for r in (res.data or [])]


def list_for_doctor(doctor_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("bookings")
        .select(_SELECT)
        .eq("doctor_id", doctor_id)
        .order("starts_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return [_flatten(r) for r in (res.data or [])]


def update_status(booking_id: str, new_status: str) -> dict | None:
    db = get_service_client()
    res = db.table("bookings").update({"status": new_status}).eq("id", booking_id).execute()
    if not res.data:
        return None
    return get_booking(booking_id)