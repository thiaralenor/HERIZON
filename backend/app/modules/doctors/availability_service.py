from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.db.supabase_client import get_service_client

DEFAULT_TZ = "Africa/Douala"  # adjust to your target market


def list_availability(doctor_id: str) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("doctor_availability")
        .select("*")
        .eq("doctor_id", doctor_id)
        .order("weekday")
        .order("start_time")
        .execute()
    )
    return res.data or []


def replace_availability(doctor_id: str, rows: list[dict]) -> list[dict]:
    db = get_service_client()
    db.table("doctor_availability").delete().eq("doctor_id", doctor_id).execute()
    if rows:
        for r in rows:
            r["doctor_id"] = doctor_id
        db.table("doctor_availability").insert(rows).execute()
    return list_availability(doctor_id)


def list_time_off(doctor_id: str) -> list[dict]:
    db = get_service_client()
    res = (
        db.table("doctor_time_off")
        .select("*")
        .eq("doctor_id", doctor_id)
        .order("starts_at")
        .execute()
    )
    return res.data or []


def add_time_off(doctor_id: str, payload: dict) -> dict:
    db = get_service_client()
    payload["doctor_id"] = doctor_id
    return db.table("doctor_time_off").insert(payload).execute().data[0]


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def generate_slots(
    doctor_id: str,
    from_date: date,
    to_date: date,
    tz_name: str = DEFAULT_TZ,
) -> dict:
    """
    Produce all slots in the range, marking each as available or not.
    Availability = weekly rule covers it AND no time-off overlaps AND no active booking.
    """
    if to_date < from_date:
        raise ValueError("to_date must be >= from_date")
    if (to_date - from_date).days > 60:
        raise ValueError("Range too large (max 60 days)")

    tz = ZoneInfo(tz_name)
    db = get_service_client()

    rules = list_availability(doctor_id)
    time_off = list_time_off(doctor_id)

    range_start = datetime.combine(from_date, time.min, tzinfo=tz)
    range_end = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=tz)

    booked = (
        db.table("bookings")
        .select("starts_at, ends_at")
        .eq("doctor_id", doctor_id)
        .in_("status", ["pending", "confirmed"])
        .gte("starts_at", range_start.isoformat())
        .lt("starts_at", range_end.isoformat())
        .execute()
        .data
        or []
    )
    booked_ranges = [
        (datetime.fromisoformat(b["starts_at"]), datetime.fromisoformat(b["ends_at"]))
        for b in booked
    ]

    out_slots: list[dict] = []
    day = from_date
    while day <= to_date:
        weekday = day.isoweekday() % 7        # Sun=0 ... Sat=6
        for rule in rules:
            if rule["weekday"] != weekday:
                continue
            slot_len = timedelta(minutes=rule["slot_minutes"])
            cursor = datetime.combine(
                day, time.fromisoformat(rule["start_time"]), tzinfo=tz
            )
            rule_end = datetime.combine(
                day, time.fromisoformat(rule["end_time"]), tzinfo=tz
            )
            while cursor + slot_len <= rule_end:
                s, e = cursor, cursor + slot_len
                available = True

                for off_start, off_end in [
                    (datetime.fromisoformat(o["starts_at"]), datetime.fromisoformat(o["ends_at"]))
                    for o in time_off
                ]:
                    if _overlaps(s, e, off_start, off_end):
                        available = False
                        break

                if available:
                    for b_start, b_end in booked_ranges:
                        if _overlaps(s, e, b_start, b_end):
                            available = False
                            break

                out_slots.append(
                    {
                        "starts_at": s.isoformat(),
                        "ends_at": e.isoformat(),
                        "available": available,
                    }
                )
                cursor += slot_len
        day += timedelta(days=1)

    return {
        "doctor_id": doctor_id,
        "from_date": from_date,
        "to_date": to_date,
        "timezone": tz_name,
        "slots": out_slots,
    }