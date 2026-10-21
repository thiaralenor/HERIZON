from app.db.supabase_client import get_service_client


def list_hospitals(
    city: str | None = None,
    internship_open: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    db = get_service_client()
    q = db.table("hospitals").select("*").order("name").range(offset, offset + limit - 1)
    if city:
        q = q.eq("city", city)
    if internship_open is not None:
        q = q.eq("internship_open", internship_open)
    return q.execute().data or []


def get_hospital(hospital_id: str) -> dict | None:
    db = get_service_client()
    res = db.table("hospitals").select("*").eq("id", hospital_id).maybe_single().execute()
    return res.data if res else None


def create_hospital(payload: dict, admin_id: str) -> dict:
    db = get_service_client()
    payload["created_by"] = admin_id
    return db.table("hospitals").insert(payload).execute().data[0]


def update_hospital(hospital_id: str, payload: dict) -> dict | None:
    db = get_service_client()
    res = db.table("hospitals").update(payload).eq("id", hospital_id).execute()
    return res.data[0] if res.data else None


def set_internship(hospital_id: str, open_: bool) -> dict | None:
    return update_hospital(hospital_id, {"internship_open": open_})

def get_hospital_by_admin(admin_id: str) -> dict | None:
    db = get_service_client()
    res = (
        db.table("hospitals")
        .select("id")
        .eq("created_by", admin_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None