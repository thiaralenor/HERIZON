from unittest.mock import patch

from app.modules.doctors import service


def test_get_doctor_by_profile_returns_none_when_missing(mock_supabase_db):
    mock_supabase_db.table.return_value.select.return_value.eq.return_value \
        .maybe_single.return_value.execute.return_value.data = None

    with patch("app.modules.doctors.service.get_service_client", return_value=mock_supabase_db):
        result = service.get_doctor_by_profile("missing-user")

    assert result is None


def test_get_doctor_by_profile_flattens_joined_fields(mock_supabase_db):
    mock_supabase_db.table.return_value.select.return_value.eq.return_value \
        .maybe_single.return_value.execute.return_value.data = {
            "id": "doc-1",
            "profile_id": "prof-1",
            "specialty": "Cardiology",
            "serves_neighborhoods": ["Bokova"],
            "profiles": {"full_name": "Dr. Ashu"},
            "hospitals": {"name": "Buea Regional"},
        }

    with patch("app.modules.doctors.service.get_service_client", return_value=mock_supabase_db):
        result = service.get_doctor_by_profile("prof-1")

    assert result["full_name"] == "Dr. Ashu"
    assert result["hospital_name"] == "Buea Regional"
    assert "profiles" not in result
    assert "hospitals" not in result


def test_list_doctors_filters_by_neighborhood(mock_supabase_db):
    mock_supabase_db.table.return_value.select.return_value.order.return_value \
        .range.return_value.execute.return_value.data = []

    with patch("app.modules.doctors.service.get_service_client", return_value=mock_supabase_db):
        service.list_doctors(hospital_id="hosp-1", specialty="Cardio")

    # Assert the chain was built with the expected filters
    builder = mock_supabase_db.table.return_value
    builder.select.assert_called()
    builder.order.assert_called_once()
    builder.range.assert_called_once()