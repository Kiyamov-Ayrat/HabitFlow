from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.user import UserCreate, TokenResponse


async def register_user(data: UserCreate, db: AsyncSession) -> User:
    """Регистрация пользователя, проверка не занятости email,
    хэшируем, сохраняем"""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError(f"Email {data.email} already exists")

    user = User(
        name = data.name,
        email = data.email,
        hashed_password = hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    return user

async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    """Логин, проверка логина и пароля"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is disabled")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token = access_token,
        refresh_token = refresh_token,
    )

async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
    """Обновление токена"""
    from jose import JWTError

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise UnauthorizedError("Invalid or expired refresh token")

    #Проверка на refresh token
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError("User is not active or found")

    return TokenResponse(
        access_token = create_access_token(user.id),
        refresh_token = create_refresh_token(user.id),
    )

async def get_current_user(token: str, db: AsyncSession) -> User:
    """Dependency для защищенных пользователей
    Декодирет access token и возвращает текущего пользователя
    """
    from jose import JWTError
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError("Invalid or expired access token")
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError("User is not active or found")
    return user
