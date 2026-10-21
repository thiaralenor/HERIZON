from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HospitalBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    emergency_line: str | None = None


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    emergency_line: str | None = None


class InternshipToggle(BaseModel):
    internship_open: bool


class HospitalOut(HospitalBase):
    id: UUID
    internship_open: bool
    created_by: UUID | None = None
    created_at: datetime