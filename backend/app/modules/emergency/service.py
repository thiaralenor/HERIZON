from app.db.supabase_client import get_service_client

# Static national numbers as currently published. The 119 line is the officially
# defined SAMU number; 1510 is the line PHEC actually answers on. We surface both.
STATIC_CONTACTS = [
    {"label": "SAMU (national emergency)", "phone": "119", "kind": "samu"},
    {"label": "PHEC (emergency coordination)", "phone": "1510", "kind": "samu"},
    {"label": "Regional emergency ops (Buea)", "phone": "670782967", "kind": "regional_ops"},
]


def get_contacts(hospital_id: str | None = None) -> dict:
    contacts = list(STATIC_CONTACTS)
    if hospital_id:
        db = get_service_client()
        res = (
            db.table("hospitals")
            .select("name, emergency_line, phone")
            .eq("id", hospital_id)
            .maybe_single()
            .execute()
        )
        if res and res.data:
            h = res.data
            line = h.get("emergency_line") or h.get("phone")
            if line:
                contacts.insert(
                    0,
                    {
                        "label": f"{h['name']} (direct)",
                        "phone": line,
                        "kind": "hospital",
                    },
                )
    return {"contacts": contacts, "hospital_id": hospital_id}


def create_sos(user_id: str, payload: dict) -> dict:
    db = get_service_client()
    row = {
        "user_id": user_id,
        "hospital_id": payload.get("hospital_id"),
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
    }
    return db.table("sos_logs").insert(row).execute().data[0]