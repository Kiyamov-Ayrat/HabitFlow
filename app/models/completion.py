from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Completion(Base):
    __tablename__ = "completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(sa.ForeginKey(
        "habits.id", ondelete="CASCADE"), nullable=False, index=True)
    # Дата выполнения храним с timezone
    completed_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
    )
    # Опциональная заметка
    note: Mapped[str | None] = mapped_column(sa.Text())

    habit: Mapped["Habit"] = relationship(back_populates="completions")

    # Уникальность: одна привычка - одна отметка в день
    __table_args__ = (
        sa.UniqueConstraint("habit_id",
                            sa.func.date("completed_at"),
                            name="uq_completion_per_day"),
    )