

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

"""Pydantic schemas for freelance clinicians."""


class FreelancerCreate(BaseModel):
    specialty: str = Field(min_length=1, max_length=120)
    bio: str | None = None
    consultation_fee: float | None = Field(default=None, ge=0)
    slug: str = Field(
        min_length=2,
        max_length=80,
        pattern=r"^[a-z0-9-]+$",
    )
    serves_neighborhoods: list[str] = Field(default_factory=list)


class FreelancerUpdate(BaseModel):
    specialty: str | None = Field(
        default=None, min_length=1, max_length=120
    )
    bio: str | None = None
    consultation_fee: float | None = Field(default=None, ge=0)
    is_active: bool | None = None
    serves_neighborhoods: list[str] | None = None


class FreelancerOut(BaseModel):
    id: UUID
    profile_id: UUID
    full_name: str | None = None
    doctor_type: str
    hospital_id: UUID | None = None
    hospital_name: str | None = None
    specialty: str
    bio: str | None = None
    consultation_fee: float | None = None
    slug: str
    is_active: bool
    serves_neighborhoods: list[str] = Field(default_factory=list)
    created_at: datetime
