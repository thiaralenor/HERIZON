from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AvailabilityIn(BaseModel):
    weekday: int = Field(ge=0, le=6)          # 0=Sunday
    start_time: time
    end_time: time
    slot_minutes: int = Field(default=30, ge=5, le=240)

    @model_validator(mode="after")
    def _check_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AvailabilityOut(AvailabilityIn):
    id: UUID
    doctor_id: UUID


class TimeOffIn(BaseModel):
    starts_at: datetime
    ends_at: datetime
    reason: str | None = None

    @model_validator(mode="after")
    def _check_order(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class TimeOffOut(TimeOffIn):
    id: UUID
    doctor_id: UUID


class SlotOut(BaseModel):
    starts_at: datetime
    ends_at: datetime
    available: bool


class SlotsResponse(BaseModel):
    doctor_id: UUID
    from_date: date
    to_date: date
    timezone: str
    slots: list[SlotOut]