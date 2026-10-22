
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_role
from app.core.security import CurrentUser
from app.modules.freelancers import service
from app.modules.freelancers.schemas import (
    FreelancerCreate,
    FreelancerOut,
    FreelancerUpdate,
)


router = APIRouter(prefix="/freelancers", tags=["freelancers"])


@router.get("", response_model=list[FreelancerOut])
def list_freelancers(
    specialty: str | None = Query(None),
    neighborhood: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_freelancers(
        specialty=specialty,
        neighborhood=neighborhood,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=FreelancerOut)
def get_my_freelancer_profile(
    user: CurrentUser = Depends(require_role("freelancer")),
):
    freelancer = service.get_freelancer_by_profile(user.id)

    if not freelancer:
        raise HTTPException(
            status_code=404,
            detail="Freelancer profile not found",
        )

    return freelancer


@router.post(
    "/me",
    response_model=FreelancerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_my_freelancer_profile(
    payload: FreelancerCreate,
    user: CurrentUser = Depends(require_role("freelancer")),
):
    return service.create_freelancer(
        payload.model_dump(exclude_none=True),
        user.id,
    )


@router.patch("/me", response_model=FreelancerOut)
def update_my_freelancer_profile(
    payload: FreelancerUpdate,
    user: CurrentUser = Depends(require_role("freelancer")),
):
    freelancer = service.update_freelancer(
        user.id,
        payload.model_dump(exclude_unset=True),
    )

    if not freelancer:
        raise HTTPException(
            status_code=404,
            detail="Freelancer profile not found",
        )

    return freelancer


@router.get("/by-slug/{slug}", response_model=FreelancerOut)
def get_freelancer_by_slug(slug: str):
    freelancer = service.get_freelancer_by_slug(slug)

    if not freelancer:
        raise HTTPException(
            status_code=404,
            detail="Freelancer not found",
        )

    return freelancer


@router.get("/{freelancer_id}", response_model=FreelancerOut)
def get_freelancer(freelancer_id: str):
    freelancer = service.get_freelancer_by_id(freelancer_id)

    if not freelancer:
        raise HTTPException(
            status_code=404,
            detail="Freelancer not found",
        )

    return freelancer
