from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.emergency import service
from app.modules.emergency.schemas import (
    EmergencyContactsResponse,
    SOSCreate,
)

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.get("/contacts", response_model=EmergencyContactsResponse)
def emergency_contacts(
    hospital_id: str | None = Query(None),
    user: CurrentUser = Depends(require_role("patient", "doctor", "freelancer")),
):
    return service.get_contacts(hospital_id)


@router.post("/sos", status_code=status.HTTP_201_CREATED)
def log_sos(
    payload: SOSCreate,
    user: CurrentUser = Depends(require_role("patient")),
):
    return service.create_sos(user.id, payload.model_dump(exclude_none=True))