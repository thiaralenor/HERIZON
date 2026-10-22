from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DoctorCreate(BaseModel):
    doctor_type: str = Field(pattern="^(hospital|freelance)$")
    hospital_id: UUID | None = None
    specialty: str = Field(min_length=1, max_length=120)
    bio: str | None = None
    consultation_fee: float | None = None
    slug: str = Field(min_length=2, max_length=80, pattern="^[a-z0-9-]+$")


class DoctorUpdate(BaseModel):
    specialty: str | None = None
    bio: str | None = None
    consultation_fee: float | None = None
    is_active: bool | None = None


class DoctorOut(BaseModel):
    id: UUID
    profile_id: UUID
    full_name: str | None = None
    doctor_type: str
    hospital_id: UUID | None
    hospital_name: str | None = None
    specialty: str
    bio: str | None
    consultation_fee: float | None
    slug: str
    is_active: bool
    serves_neighborhoods: list[str] = []      # ← new
    created_at: datetime
