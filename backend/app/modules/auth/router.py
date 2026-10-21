from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import CurrentUser, get_current_user
from app.modules.auth.schemas import MeOut, ProfileOut
from app.modules.auth.service import fetch_admin_hospital, fetch_doctor_link, fetch_profile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser = Depends(get_current_user)) -> MeOut:
    profile = fetch_profile(user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete signup first.",
        )

    doctor_id = None
    hospital_id = None

    if user.role in ("doctor", "freelancer"):
        doctor = fetch_doctor_link(user.id)
        if doctor:
            doctor_id = doctor["id"]
            hospital_id = doctor["hospital_id"]
    elif user.role == "hospital_admin":
        hospital = fetch_admin_hospital(user.id)
        if hospital:
            hospital_id = hospital["id"]

    return MeOut(
        profile=ProfileOut(**profile),
        doctor_id=doctor_id,
        hospital_id=hospital_id,
    )