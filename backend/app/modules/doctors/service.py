from app.db.supabase_client import get_service_client

# Supabase's PostgREST lets us embed related rows in one query — this is what
# we use to join doctors -> profiles (name) and doctors -> hospitals (name).
# backend/app/modules/doctors/service.py — add to _SELECT string
_SELECT = (
    "id, profile_id, doctor_type, hospital_id, specialty, bio, "
    "consultation_fee, slug, is_active, created_at, serves_neighborhoods, "
    "profiles:profile_id(full_name), hospitals:hospital_id(name)"
)


def _flatten(row: dict) -> dict:
    profiles = row.pop("profiles", None) or {}
    hospitals = row.pop("hospitals", None) or {}
    row["full_name"] = profiles.get("full_name")
    row["hospital_name"] = hospitals.get("name")
    return row


def list_doctors(
    *,
    doctor_type: str | None = None,
    hospital_id: str | None = None,
    specialty: str | None = None,
    search: str | None = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    db = get_service_client()
    q = (
        db.table("doctors")
        .select(_SELECT)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if active_only:
        q = q.eq("is_active", True)
    if doctor_type:
        q = q.eq("doctor_type", doctor_type)
    if hospital_id:
        q = q.eq("hospital_id", hospital_id)
    if specialty:
        q = q.ilike("specialty", f"%{specialty}%")
    if search:
        # name search across joined profile — uses a filter on the embedded table
        q = q.ilike("profiles.full_name", f"%{search}%")
    rows = q.execute().data or []
    return [_flatten(r) for r in rows]


def get_doctor_by_id(doctor_id: str) -> dict | None:
    db = get_service_client()
    res = db.table("doctors").select(_SELECT).eq("id", doctor_id).maybe_single().execute()
    return _flatten(res.data) if res and res.data else None


def get_doctor_by_slug(slug: str) -> dict | None:
    db = get_service_client()
    res = db.table("doctors").select(_SELECT).eq("slug", slug).maybe_single().execute()
    return _flatten(res.data) if res and res.data else None


def get_doctor_by_profile(profile_id: str) -> dict | None:
    db = get_service_client()
    res = (
        db.table("doctors")
        .select(_SELECT)
        .eq("profile_id", profile_id)
        .maybe_single()
        .execute()
    )
    return _flatten(res.data) if res and res.data else None


def create_doctor(payload: dict, profile_id: str) -> dict:
    db = get_service_client()
    payload["profile_id"] = profile_id
    # DB CHECK constraint will reject inconsistent hospital_id/doctor_type combos
    row = db.table("doctors").insert(payload).execute().data[0]
    return get_doctor_by_id(row["id"])


def update_doctor(doctor_id: str, payload: dict) -> dict | None:
    db = get_service_client()
    if payload:
        db.table("doctors").update(payload).eq("id", doctor_id).execute()
    return get_doctor_by_id(doctor_id)