from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DispatchCreate(BaseModel):
    hospital_id: UUID | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    note: str | None = Field(default=None, max_length=500)


class DispatchPositionOut(BaseModel):
    lat: float
    lng: float
    recorded_at: datetime


class DispatchOut(BaseModel):
    id: UUID
    patient_id: UUID
    hospital_id: UUID | None
    hospital_name: str | None = None
    ambulance_id: UUID | None
    ambulance_call_sign: str | None = None
    status: str
    patient_lat: float | None
    patient_lng: float | None
    note: str | None
    created_at: datetime
    updated_at: datetime