from datetime import time
from pydantic import BaseModel

class HabitCreate(BaseModel):
    """Данные для создания привычки"""
    title: str
    description: str | None = None
    frequency: str = "daily"
    reminder_time: time | None = None

class HabitUpdate(BaseModel):
    """Поля опциональные, обновляется то что передали"""
    title: str | None = None
    description: str | None = None
    frequency: str | None = None
    reminder_time: time | None = None
    is_active: bool | None = None

class HabitResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    frequency: str | None = None
    reminder_time: time | None
    is_active: bool

    model_config = {"from_attributes": True}

