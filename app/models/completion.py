from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Completion(Base):
    __tablename__ = "completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        sa.ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
    )
    note: Mapped[str | None] = mapped_column(sa.Text)

    habit: Mapped["Habit"] = relationship(back_populates="completions")

    # UniqueConstraint принимает только имена колонок строками.
    # Уникальность по дню реализуем на уровне сервиса, не БД —
    # это надёжнее и переносимее между разными СУБД
    __table_args__ = (
        sa.Index("ix_completion_habit_date", "habit_id", "completed_at"),
    )