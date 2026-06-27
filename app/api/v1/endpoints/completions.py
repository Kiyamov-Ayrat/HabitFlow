from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.deps import current_user
from app.db.session import get_db
from app.db.redis import get_redis
from app.models.user import User
from app.schemas.completion import CompletionCreate, CompletionResponse
from app.services import completion as completion_service
from app.services.stats import invalidate_stats_cache

router = APIRouter()

@router.get("/{habit_id}", response_model = list[CompletionResponse])
async def get_completions(
        habit_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    """Получить историю выполнений привычки"""
    return await completion_service.get_habit_completions(habit_id, user, db)

@router.post("/{habit_id}", response_model=CompletionResponse, status_code=201)
async def mark_complete(
        habit_id: int,
        data: CompletionCreate,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    """Отметить привычку выполненной на сегодня"""
    completion = await completion_service.mark_complete(habit_id, data, user, db)
    # Сбрасываем кэш статистики данные изменились
    await invalidate_stats_cache(user.id, redis)
    return completion


@router.delete("/{habit_id}", status_code=204)
async def unmark_complete(
        habit_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    """Снимаем отметку выполнения за сегодня"""
    await completion_service.unmark_complete(habit_id, user, db)
    await invalidate_stats_cache(user.id, redis)