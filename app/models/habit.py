from datetime import datetime, time

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeginKey("users.id", ondelete="CASCADE"),
                                         nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)

    # Как часто нужно выполнять daily/weekly
    frequency: Mapped[int] = mapped_column(sa.String(20), default="daily")

    # Время напоминаяни, None - без напоминания
    reminder_time: Mapped[time | None] = mapped_column(sa.Time)
    is_active: Mapped[bool] =mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
    )

    # Связь с владельцем
    user: Mapped["User"] = relationship(back_populates="habits")
    # Связь с отметками выполнения
    completions: Mapped[list["Completion"]] = relationship(back_populates="habit",
                                                           cascade="all, delete-orphan")
