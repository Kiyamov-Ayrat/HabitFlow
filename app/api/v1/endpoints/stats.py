from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.deps import current_user
from app.db.session import get_db
from app.db.redis import get_redis
from app.models.user import User
from app.schemas.stats import StatsResponse
from app.services.stats import get_user_stats

router = APIRouter()

@router.get("/", response_model=StatsResponse)
async def get_stats(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    """Статистика по всем привычкам
    Результат кэшируем на 5 минут"""
    return await get_user_stats(user, db, redis)
