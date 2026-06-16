from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    # Часовой пояс пользователя — нужен чтобы слать напоминания в правильное время
    timezone: Mapped[str] = mapped_column(sa.String(50), default="UTC")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),  # БД сама ставит время, не Python
    )

    # Связь один-ко-многим: у одного юзера много привычек
    habits: Mapped[list["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")