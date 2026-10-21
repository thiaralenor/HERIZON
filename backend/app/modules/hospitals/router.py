from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.hospitals import service
from app.modules.hospitals.schemas import (
    HospitalCreate,
    HospitalOut,
    HospitalUpdate,
    InternshipToggle,
)

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("", response_model=list[HospitalOut])
def list_hospitals(
    city: str | None = Query(None),
    internship_open: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_hospitals(city, internship_open, limit, offset)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital(hospital_id: str):
    h = service.get_hospital(hospital_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return h


@router.post("", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
def create_hospital(
    payload: HospitalCreate,
    user: CurrentUser = Depends(require_role("hospital_admin")),
):
    # Ensure this admin doesn't already own a hospital
    if service.get_hospital_by_admin(user.id):
        raise HTTPException(status_code=409, detail="Admin already owns a hospital")
    return service.create_hospital(payload.model_dump(exclude_none=True), user.id)


@router.patch("/{hospital_id}", response_model=HospitalOut)
def update_hospital(
    hospital_id: str,
    payload: HospitalUpdate,
    user: CurrentUser = Depends(require_role("hospital_admin")),
):
    hospital = service.get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    if hospital["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not your hospital")
    updated = service.update_hospital(hospital_id, payload.model_dump(exclude_none=True))
    return updated


@router.patch("/{hospital_id}/internship", response_model=HospitalOut)
def toggle_internship(
    hospital_id: str,
    payload: InternshipToggle,
    user: CurrentUser = Depends(require_role("hospital_admin")),
):
    hospital = service.get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    if hospital["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not your hospital")
    # Trigger in 0007 fires when flipping false -> true, notifying doctors
    return service.set_internship(hospital_id, payload.internship_open)