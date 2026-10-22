from app.db.supabase_client import get_service_client

_SELECT = (
    "id, patient_id, hospital_id, ambulance_id, status, patient_lat, patient_lng, "
    "note, created_at, updated_at, "
    "hospitals:hospital_id(name), ambulances:ambulance_id(call_sign)"
)


def _flatten(row: dict) -> dict:
    h = row.pop("hospitals", None) or {}
    a = row.pop("ambulances", None) or {}
    row["hospital_name"] = h.get("name")
    row["ambulance_call_sign"] = a.get("call_sign")
    return row


def _pick_nearest_available(db, hospital_id: str | None) -> dict | None:
    q = db.table("ambulances").select("*").eq("status", "available")
    if hospital_id:
        q = q.eq("hospital_id", hospital_id)
    res = q.limit(1).execute()
    return res.data[0] if res and res.data else None


def create_dispatch(patient_id: str, payload: dict) -> dict:
    db = get_service_client()

    # 1. pick an ambulance
    amb = _pick_nearest_available(db, payload.get("hospital_id"))

    dispatch_row = {
        "patient_id": patient_id,
        "hospital_id": payload.get("hospital_id") or (amb["hospital_id"] if amb else None),
        "patient_lat": payload["latitude"],
        "patient_lng": payload["longitude"],
        "note": payload.get("note"),
        "status": "pending",
    }
    dispatch = db.table("dispatch_requests").insert(dispatch_row).execute().data[0]

    if not amb:
        db.table("dispatch_requests").update({"status": "failed"}).eq(
            "id", dispatch["id"]
        ).execute()
        return get_dispatch(dispatch["id"])

    # 2. assign the ambulance and mark it busy
    db.table("dispatch_requests").update(
        {"ambulance_id": amb["id"], "status": "assigned"}
    ).eq("id", dispatch["id"]).execute()
    db.table("ambulances").update({"status": "en_route"}).eq("id", amb["id"]).execute()

    return get_dispatch(dispatch["id"])


def get_dispatch(dispatch_id: str) -> dict | None:
    db = get_service_client()
    res = (
        db.table("dispatch_requests")
        .select(_SELECT)
        .eq("id", dispatch_id)
        .maybe_single()
        .execute()
    )
    return _flatten(res.data) if res and res.data else None


def list_for_patient(patient_id: str, limit: int = 20) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("dispatch_requests")
        .select(_SELECT)
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return [_flatten(r) for r in (res.data or [])]


def list_positions(dispatch_id: str) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("dispatch_positions")
        .select("lat, lng, recorded_at")
        .eq("dispatch_request_id", dispatch_id)
        .order("recorded_at")
        .execute()
    )
    return res.data or []


def simulate_tick(dispatch_id: str) -> dict | None:
    """Path A only: advance the simulated ambulance one step."""
    db = get_service_client()
    db.rpc("simulate_dispatch_step", {"p_dispatch_id": dispatch_id}).execute()
    return get_dispatch(dispatch_id)

def simulate_tick(dispatch_id: str) -> dict | None:
    db = get_service_client()
    before = get_dispatch(dispatch_id)
    db.rpc("simulate_dispatch_step", {"p_dispatch_id": dispatch_id}).execute()
    after = get_dispatch(dispatch_id)

    if before and after and before["status"] != after["status"]:
        from app.modules.notifications.service import create_notification

        title_map = {
            "en_route": "Ambulance en route",
            "arrived": "Ambulance has arrived",
        }
        if after["status"] in title_map:
            create_notification(
                user_id=after["patient_id"],
                type_=f"dispatch_{after['status']}",
                title=title_map[after["status"]],
                body=f"Dispatch {dispatch_id}",
                data={"dispatch_id": dispatch_id},
            )

    return after


def cancel_dispatch(dispatch_id: str, patient_id: str) -> dict | None:
    db = get_service_client()
    current = get_dispatch(dispatch_id)
    if not current:
        return None
    if current["patient_id"] != patient_id:
        return None
    if current["status"] in ("arrived", "cancelled", "failed"):
        return current

    db.table("dispatch_requests").update({"status": "cancelled"}).eq(
        "id", dispatch_id
    ).execute()
    if current["ambulance_id"]:
        db.table("ambulances").update({"status": "available"}).eq(
            "id", current["ambulance_id"]
        ).execute()
    return get_dispatch(dispatch_id)

def list_for_hospital(hospital_id: str, limit: int = 50) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("dispatch_requests")
        .select(_SELECT)
        .eq("hospital_id", hospital_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return [_flatten(r) for r in (res.data or [])]


def get_admin_hospital(user_id: str) -> dict | None:
    db = get_service_client()
    res = (
        db.table("hospitals")
        .select("id, name")
        .eq("created_by", user_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None