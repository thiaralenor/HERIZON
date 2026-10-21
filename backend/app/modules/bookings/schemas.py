from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BookingCreate(BaseModel):
    doctor_id: UUID
    starts_at: datetime
    ends_at: datetime
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _check_order(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class BookingOut(BaseModel):
    id: UUID
    doctor_id: UUID
    doctor_name: str | None = None
    doctor_slug: str | None = None
    patient_id: UUID
    patient_name: str | None = None
    starts_at: datetime
    ends_at: datetime
    status: str
    reason: str | None
    created_at: datetime


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(cancelled|completed|no_show)$")