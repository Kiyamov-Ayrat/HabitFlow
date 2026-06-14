from redis.asyncio import Redis, from_url

from app.core.settings import settings

# Пул соединения с Redis
redis_client: Redis = from_url(
    settings.redis_url,
    decode_responses=True,
    encoding="utf-8",
)

async def get_redis() -> Redis:
    """
    Внедряется через Depends(get_redis)
    Использование в эндпоинте:
        async def endpoint(redis: Redis = Depends(get_redis)):
    """
    return redis_client