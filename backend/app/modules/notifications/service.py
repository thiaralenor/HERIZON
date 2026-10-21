from app.db.supabase_client import get_service_client


def list_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    db = get_service_client()
    q = (
        db.table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if unread_only:
        q = q.is_("read_at", "null")
    return q.execute().data or []


def count_unread(user_id: str) -> int:
    db = get_service_client()
    res = (
        db.table("notifications")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .is_("read_at", "null")
        .execute()
    )
    return res.count or 0


def mark_read(user_id: str, notification_id: str) -> dict | None:
    db = get_service_client()
    from datetime import datetime, timezone

    res = (
        db.table("notifications")
        .update({"read_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", notification_id)
        .eq("user_id", user_id)
        .execute()
    )
    return res.data[0] if res.data else None


def mark_all_read(user_id: str) -> int:
    db = get_service_client()
    from datetime import datetime, timezone

    res = (
        db.table("notifications")
        .update({"read_at": datetime.now(timezone.utc).isoformat()})
        .eq("user_id", user_id)
        .is_("read_at", "null")
        .execute()
    )
    return len(res.data or [])


def create_notification(
    user_id: str,
    type_: str,
    title: str,
    body: str | None = None,
    data: dict | None = None,
) -> dict:
    """Internal helper — called by other services when an event fires."""
    db = get_service_client()
    row = {
        "user_id": user_id,
        "type": type_,
        "title": title,
        "body": body,
        "data": data or {},
    }
    return db.table("notifications").insert(row).execute().data[0]