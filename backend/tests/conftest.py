import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_supabase_db():
    """
    Returns a MagicMock that mimics the Supabase chained-query builder.

    Usage:
        db = mock_supabase_db
        db.table("doctors").select("*").eq("id", "x").execute.return_value.data = [...]
    """
    db = MagicMock()
    # Each .table() call returns a new builder so tests can configure per-table
    builder = MagicMock()
    builder.select.return_value = builder
    builder.insert.return_value = builder
    builder.update.return_value = builder
    builder.delete.return_value = builder
    builder.eq.return_value = builder
    builder.neq.return_value = builder
    builder.is_.return_value = builder
    builder.in_.return_value = builder
    builder.gte.return_value = builder
    builder.lt.return_value = builder
    builder.ilike.return_value = builder
    builder.order.return_value = builder
    builder.range.return_value = builder
    builder.limit.return_value = builder
    builder.maybe_single.return_value = builder
    builder.rpc.return_value = builder
    builder.execute.return_value = MagicMock(data=[], count=0)
    db.table.return_value = builder
    db.rpc.return_value = builder
    return db


@pytest.fixture
def local_supabase():
    """Real local Supabase client. Only available when RUN_INTEGRATION=1."""
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests require RUN_INTEGRATION=1 and `supabase start`")

    from supabase import create_client

    url = os.getenv("LOCAL_SUPABASE_URL", "http://127.0.0.1:54321")
    key = os.getenv(
        "LOCAL_SUPABASE_SERVICE_KEY",
        # default local service key — see `supabase status`
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    return create_client(url, key)