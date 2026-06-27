from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitUpdate

async def get_user_habits(user: User, db: AsyncSession) -> list[Habit]:
    """Получить все привычки пользователя"""
    result = await db.execute(
        select(Habit)
        .where(Habit.user_id == user.id)
        .order_by(Habit.created_at.desc())
    )
    return list(result.scalars().all())

async def get_habit_by_id(habit_id: int, user: User, db: AsyncSession) -> Habit:
    """Получить привычку по id"""
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id)
    )
    habit = result.scalar_one_or_none()

    if not habit:
        raise NotFoundError(f"Habit {habit_id} not found")

    # Данные чужого пользователя
    if habit.user_id != user.id:
        raise ForbiddenError("Access denied")

    return habit

async def create_habit(data: HabitCreate, user: User, db: AsyncSession) -> Habit:
    """Создание новой привычки"""
    habit = Habit(
        user_id = user.id,
        title=data.title,
        description=data.frequency,
        reminder_time=data.reminder_time,
    )

    db.add(habit)
    await db.flush()
    return habit

async def update_habit(
        habit_id: int,
        data: HabitUpdate,
        user: User,
        db: AsyncSession,
) -> Habit:
    """Изменяем привычку, меняются только переданные поля"""
    habit = await get_habit_by_id(habit_id, user, db)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    await db.flush()
    return habit

async def delete_habit(habit_id: int, user: User, db: AsyncSession) -> None:
    """Удалить привычку, установлен cascade delete"""
    habit = await get_habit_by_id(habit_id, user, db)
    await db.delete(habit)
    await db.flush()
