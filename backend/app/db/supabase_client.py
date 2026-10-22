
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create and reuse the Supabase client."""

    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL is missing from .env.")

    if not settings.supabase_anon_key:
        raise RuntimeError("SUPABASE_ANON_KEY is missing from .env.")

    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )
