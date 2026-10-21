from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.core.security import CurrentUser, get_current_user


def require_role(*allowed: str):
    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role in {allowed}, got '{user.role}'",
            )
        return user

    return _dep


DoctorUser = Depends(require_role("doctor", "freelancer"))
PatientUser = Depends(require_role("patient"))
HospitalAdminUser = Depends(require_role("hospital_admin"))
AnyUser = Depends(get_current_user)
