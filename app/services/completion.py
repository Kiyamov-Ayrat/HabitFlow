from datetime import date, datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.models.completion import Completion
from app.models.habit import Habit
from app.models.user import User
from app.schemas.completion import CompletionCreate

async def get_habit_completions(
        habit_id: int,
        user: User,
        db: AsyncSession,
) -> list[Completion]:
    """Получить все отметки выполнения для привычки"""
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id)
    )
    habit = result.scalar_one_or_none()

    if not habit:
        raise NotFoundError(f"Habit {habit_id} not found")

    if habit.user_id != user.id:
        raise ForbiddenError(f"Access denied")

    result = await db.execute(
        select(Completion)
        .where(Completion.habit_id == habit_id)
        .order_by(Completion.completed_at.desc())
    )
    return list(result.scalars().all())

async def mark_complete(
        habit_id: int,
        data: CompletionCreate,
        user: User,
        db: AsyncSession,
) -> Completion:
    """Отметить привычку выполненной сегодня.
    Запрет на отмену одной привычки дважды в день"""

    result = await db.execute(
        select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()

    if not habit:
        raise NotFoundError(f"Habit {habit_id} not found")
    if habit.user_id != user.id:
        raise ForbiddenError(f"Access denied")

    # Проверка нет ли отметки сегодня
    today = date.today()
    result = await db.execute(
        select(Completion).where(
            Completion.habit_id == habit_id,
        #     Сравниваем дату
            func.date(Completion.completed_at) == today,
        )
    )
    if result.scalar_one_or_none():
        raise ConflictError(f"Habit {habit_id} already exists")

    completion = Completion(
        habit_id = habit_id,
        note = data.note,
        completed_at = datetime.now(timezone.utc),
    )

    db.add(completion)
    await db.flush()
    return completion

async def unmark_complete(habit_id: int, user: User, db: AsyncSession) -> None:
    """Снять отметку выполнения за сегодня"""
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id)
    )
    habit = result.scalar_one_or_none()

    if not habit:
        raise NotFoundError(f"Habit {habit_id} not found")
    if habit.user_id != user.id:
        raise ForbiddenError(f"Access denied")

    today = date.today()
    result = await db.execute(
        select(Completion).where(
            Completion.habit_id == habit_id,
            func.date(Completion.completed_at) == today,

        )
    )

    completion = result.scalar_one_or_none()

    if not completion:
        raise NotFoundError(f"Not completion found for today")

    await db.delete(completion)
    await db.flush()


def calculate_streak(completions: list[Completion]) -> dict:
    """Алгоритм подсчета серии дней
    - берем все даты выполнения, сортируем от новых к старым
    - идем назад день за днем до сегодня
    - если день пропущен текущая серия прерывается
    - заодно считаем рекордную серию за все время"""

    if not completions:
        return {"current_stresk": 0, "longest_streak": 0}

    # Собираем уникальные даты выполнения
    completion_dates = sorted(
        {c.completed_at.date() for c in completions},
        reverse = True,
    )

    today = date.today()
    current_streak = 0
    longest_streak = 0
    temp_streak = 1

    # Считаем текущую серию идем назад от сегодня
    check_date = today
    for completion_date in completion_dates:
        if completion_date == check_date:
            current_streak += 1
            # Двигаемся на день назад
            check_date = date.fromordinal(check_date.toordinal() - 1)
        else:
            break

    # Считаем рекордную серию за всё время
    for i in range(1, len(completion_dates)):
        prev = completion_dates[i - 1]
        curr = completion_dates[i]
        # Если дни идут подряд
        if (prev.toordinal() - curr.toordinal()) == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    longest_streak = max(longest_streak, current_streak)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }
