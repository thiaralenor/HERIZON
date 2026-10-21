from uuid import UUID

from pydantic import BaseModel, Field


class EmergencyContactOut(BaseModel):
    label: str
    phone: str
    kind: str                     # 'samu' | 'hospital' | 'regional_ops'


class EmergencyContactsResponse(BaseModel):
    contacts: list[EmergencyContactOut]
    hospital_id: UUID | None = None


class SOSCreate(BaseModel):
    hospital_id: UUID | None = None
    latitude: float | None = None
    longitude: float | None = None
    note: str | None = Field(default=None, max_length=500)"""Pydantic schemas for SOS event records."""