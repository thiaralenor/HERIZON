from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProfileOut(BaseModel):
    id: UUID
    role: str
    full_name: str
    phone: str | None
    created_at: datetime


class MeOut(BaseModel):
    profile: ProfileOut
    doctor_id: UUID | None = None
    hospital_id: UUID | None = None
