from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class HospitalOption(BaseModel):
	id: str
	name: str
	location: str


class ProviderOption(BaseModel):
	id: str
	name: str
	specialty: str
	hospital_id: str | None = None
	next_available: date


class BookingOptions(BaseModel):
	demo_mode: bool = True
	hospitals: list[HospitalOption]
	providers: list[ProviderOption]
	specialties: list[str]


class BookingCreate(BaseModel):
	patient_name: str = Field(min_length=2, max_length=120)
	patient_email: EmailStr
	provider_type: Literal["hospital", "freelance"]
	hospital_id: str | None = None
	doctor_id: str
	appointment_date: date
	appointment_time: str
	reason: str | None = Field(default=None, max_length=500)


class BookingReceipt(BaseModel):
	id: str
	status: Literal["requested"] = "requested"
	provider_name: str
	provider_type: Literal["hospital", "freelance"]
	hospital_name: str | None = None
	appointment_date: date
	appointment_time: str

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SymptomLogCreate(BaseModel):
    symptoms: str = Field(min_length=1, max_length=2000)
    severity: int | None = Field(default=None, ge=1, le=10)


class SymptomLogOut(BaseModel):
    id: UUID
    patient_id: UUID
    symptoms: str
    severity: int | None
    logged_at: datetime