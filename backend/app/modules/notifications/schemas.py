from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str | None
    data: dict
    read_at: datetime | None
    created_at: datetime


class UnreadCountOut(BaseModel):
    count: int