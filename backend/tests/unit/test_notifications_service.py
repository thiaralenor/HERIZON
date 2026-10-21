from unittest.mock import patch

from app.modules.notifications import service


def test_count_unread_uses_exact_count(mock_supabase_db):
    mock_supabase_db.table.return_value.select.return_value.eq.return_value \
        .is_.return_value.execute.return_value.count = 7

    with patch("app.modules.notifications.service.get_service_client", return_value=mock_supabase_db):
        assert service.count_unread("user-1") == 7


def test_mark_read_returns_none_when_not_found(mock_supabase_db):
    mock_supabase_db.table.return_value.update.return_value.eq.return_value \
        .eq.return_value.execute.return_value.data = []

    with patch("app.modules.notifications.service.get_service_client", return_value=mock_supabase_db):
        assert service.mark_read("user-1", "nope") is None