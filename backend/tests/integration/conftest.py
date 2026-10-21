import os
import uuid
from datetime import datetime, timezone

import pytest
from supabase import create_client


@pytest.fixture(scope="session")
def supabase_local():
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 and run `supabase start`")

    url = os.getenv("LOCAL_SUPABASE_URL", "http://127.0.0.1:54321")
    service_key = os.getenv("LOCAL_SUPABASE_SERVICE_KEY")
    anon_key = os.getenv("LOCAL_SUPABASE_ANON_KEY")
    assert service_key and anon_key, "Set LOCAL_SUPABASE_SERVICE_KEY and LOCAL_SUPABASE_ANON_KEY"

    service = create_client(url, service_key)
    return {"url": url, "service": service, "anon_key": anon_key}


def _create_user(supabase_local, role: str, name: str) -> dict:
    """Create an auth user + profile row; return {id, email, password, token}."""
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "test-password-123"

    created = supabase_local["service"].auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    )
    user = created.user
    # profile is auto-created by handle_new_user trigger with role from metadata — set explicitly
    supabase_local["service"].table("profiles").update(
        {"role": role, "full_name": name}
    ).eq("id", user.id).execute()

    # sign in to get an access token that carries the right identity
    anon = create_client(supabase_local["url"], supabase_local["anon_key"])
    session = anon.auth.sign_in_with_password({"email": email, "password": password})

    return {
        "id": user.id,
        "email": email,
        "password": password,
        "token": session.session.access_token,
    }


@pytest.fixture
def patient_a(supabase_local):
    return _create_user(supabase_local, "patient", "Patient A")


@pytest.fixture
def patient_b(supabase_local):
    return _create_user(supabase_local, "patient", "Patient B")


@pytest.fixture
def doctor_user(supabase_local):
    return _create_user(supabase_local, "doctor", "Doctor X")


@pytest.fixture
def hospital_admin_user(supabase_local):
    return _create_user(supabase_local, "hospital_admin", "Admin Y")


@pytest.fixture
def authed_client(supabase_local):
    """Factory: authed_client(user) -> Supabase client scoped to that user."""
    def _make(user: dict):
        client = create_client(supabase_local["url"], supabase_local["anon_key"])
        client.auth.set_session(user["token"], user["token"])  # refresh token unused in tests
        client.postgrest.auth(user["token"])
        return client
    return _make