from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from app.db.session import get_db
from app.db.redis import Redis
from app.models.user import User
from app.services.auth import get_current_user

# tokenurl - куда клиент идет за токеном
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
) -> User:
    """Внедряется в любой защищенный эндпоинт через Depends(current_user)
    Автоматически читает токен из заголовка Authorization"""
    return await get_current_user(token, db)
