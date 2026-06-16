from datetime import datetime
from pydantic import BaseModel

class CompletionCreate(BaseModel):
    """Заметка опциональная при отметке выполнения"""
    note: str | None = None

class CompletionResponse(BaseModel):
    id: int
    habit_id: int
    completed_at: datetime
    note: str | None

    model_config = {"from_attributes": True}
