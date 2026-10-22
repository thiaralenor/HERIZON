
from fastapi import HTTPException

from app.db.supabase_client import get_service_client


_SELECT = (
    "id, profile_id, doctor_type, hospital_id, specialty, bio, "
    "consultation_fee, slug, is_active, created_at, serves_neighborhoods, "
    "profiles:profile_id(full_name), hospitals:hospital_id(name)"
)


def _flatten(row: dict) -> dict:
    row = dict(row)
    profile = row.pop("profiles", None) or {}
    hospital = row.pop("hospitals", None) or {}

    row["full_name"] = profile.get("full_name")
    row["hospital_name"] = hospital.get("name")

    return row


def list_freelancers(
    *,
    specialty: str | None = None,
    neighborhood: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    db = get_service_client()

    query = (
        db.table("doctors")
        .select(_SELECT)
        .eq("doctor_type", "freelance")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if specialty:
        query = query.ilike("specialty", f"%{specialty}%")

    if neighborhood:
        query = query.contains(
            "serves_neighborhoods", [neighborhood]
        )

    if search:
        query = query.ilike(
            "profiles.full_name", f"%{search}%"
        )

    result = query.execute()
    return [_flatten(row) for row in (result.data or [])]


def get_freelancer_by_id(freelancer_id: str) -> dict | None:
    db = get_service_client()

    result = (
        db.table("doctors")
        .select(_SELECT)
        .eq("id", freelancer_id)
        .eq("doctor_type", "freelance")
        .maybe_single()
        .execute()
    )

    return _flatten(result.data) if result and result.data else None


def get_freelancer_by_slug(slug: str) -> dict | None:
    db = get_service_client()

    result = (
        db.table("doctors")
        .select(_SELECT)
        .eq("slug", slug)
        .eq("doctor_type", "freelance")
        .maybe_single()
        .execute()
    )

    return _flatten(result.data) if result and result.data else None


def get_freelancer_by_profile(profile_id: str) -> dict | None:
    db = get_service_client()

    result = (
        db.table("doctors")
        .select(_SELECT)
        .eq("profile_id", profile_id)
        .eq("doctor_type", "freelance")
        .maybe_single()
        .execute()
    )

    return _flatten(result.data) if result and result.data else None


def create_freelancer(payload: dict, profile_id: str) -> dict:
    db = get_service_client()

    if get_freelancer_by_profile(profile_id):
        raise HTTPException(
            status_code=409,
            detail="Freelancer profile already exists",
        )

    row = {
        **payload,
        "profile_id": profile_id,
        "doctor_type": "freelance",
        "hospital_id": None,
    }

    result = db.table("doctors").insert(row).execute()

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Could not create freelancer profile",
        )

    return get_freelancer_by_id(result.data[0]["id"])


def update_freelancer(
    profile_id: str, payload: dict
) -> dict | None:
    db = get_service_client()

    current = get_freelancer_by_profile(profile_id)
    if not current:
        return None

    # Only update the record owned by the authenticated freelancer.
    if payload:
        (
            db.table("doctors")
            .update(payload)
            .eq("id", str(current["id"]))
            .eq("profile_id", profile_id)
            .eq("doctor_type", "freelance")
            .execute()
        )

    return get_freelancer_by_profile(profile_id)
