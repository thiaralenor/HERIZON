from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.dispatch import service
from app.modules.dispatch.schemas import (
    DispatchCreate,
    DispatchOut,
    DispatchPositionOut,
)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post("", response_model=DispatchOut, status_code=status.HTTP_201_CREATED)
def create_dispatch(
    payload: DispatchCreate,
    user: CurrentUser = Depends(require_role("patient")),
):
    return service.create_dispatch(user.id, payload.model_dump(exclude_none=True))


@router.get("/me", response_model=list[DispatchOut])
def my_dispatches(user: CurrentUser = Depends(require_role("patient"))):
    return service.list_for_patient(user.id)


@router.get("/{dispatch_id}", response_model=DispatchOut)
def get_dispatch(
    dispatch_id: str,
    user: CurrentUser = Depends(require_role("patient", "hospital_admin")),
):
    d = service.get_dispatch(dispatch_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return d


@router.get("/{dispatch_id}/positions", response_model=list[DispatchPositionOut])
def get_positions(
    dispatch_id: str,
    user: CurrentUser = Depends(require_role("patient", "hospital_admin")),
):
    return service.list_positions(dispatch_id)


@router.post("/{dispatch_id}/tick", response_model=DispatchOut)
def tick(
    dispatch_id: str,
    user: CurrentUser = Depends(require_role("patient")),
):
    """Path A only. Frontend calls this every ~2s while a dispatch is active."""
    return service.simulate_tick(dispatch_id)


@router.post("/{dispatch_id}/cancel", response_model=DispatchOut)
def cancel(
    dispatch_id: str,
    user: CurrentUser = Depends(require_role("patient")),
):
    d = service.cancel_dispatch(dispatch_id, user.id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return d