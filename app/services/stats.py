import json
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.settings import settings
from app.models.habit import Habit
from app.models.completion import Completion
from app.models.user import User
from app.schemas.stats import StatsResponse, HabitStats
from app.services.completion import calculate_streak


async def get_user_stats(
    user: User,
    db: AsyncSession,
    redis: Redis,
) -> StatsResponse:
    """
    Статистика по всем привычкам пользователя.
    Результат кэшируем в Redis на 5 минут.
    """
    cache_key = f"stats:user:{user.id}"

    # Пробуем взять из кэша
    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        return StatsResponse(**data)

    # Кэша нет — считаем из БД
    result = await db.execute(
        select(Habit).where(Habit.user_id == user.id)
    )
    habits = list(result.scalars().all())

    habit_stats = []
    for habit in habits:
        # Загружаем все выполнения для этой привычки
        comp_result = await db.execute(
            select(Completion).where(Completion.habit_id == habit.id)
        )
        completions = list(comp_result.scalars().all())

        streak_data = calculate_streak(completions)

        # Процент выполнения за последние 30 дней
        thirty_days_ago = date.today() - timedelta(days=30)
        recent = [
            c for c in completions
            if c.completed_at.date() >= thirty_days_ago
        ]
        completion_rate = round(len(recent) / 30 * 100, 1)

        habit_stats.append(HabitStats(
            habit_id=habit.id,
            title=habit.title,
            current_streak=streak_data["current_streak"],
            longest_streak=streak_data["longest_streak"],
            total_completions=len(completions),
            completion_rate=completion_rate,
        ))

    response = StatsResponse(
        habits=habit_stats,
        total_habits=len(habits),
        active_habits=sum(1 for h in habits if h.is_active),
    )

    # Сохран в redis на cache_ttl_seconds (300 сек)
    await redis.setex(
        cache_key,
        settings.cache_ttl_seconds,
        json.dumps(response.model_dump()),
    )
    return response

async def invalidate_stats_cache(user_id: int, redis: Redis) -> None:
    """Сбрасываем кэш статистики когда данные изменились
    Вызывается после каждого mark_complete / unmark_complete"""
    await redis.delete(f"stats:user:{user_id}")
