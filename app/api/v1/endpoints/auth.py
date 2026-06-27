from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse, RefreshRequest
from app.services.auth import register_user, login_user, refresh_tokens
from app.api.deps import current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
        data: UserCreate,
        db: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя"""
    user = await register_user(data, db)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
        from_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    """Возвращаем access и refresh token"""
    return await login_user(from_data.username, from_data.password, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
        data: RefreshRequest,
        db: AsyncSession = Depends(get_db),
):
    """Получение новую пару токенов по refresh token"""
    return await refresh_tokens(data.refresh_token, db)

@router.get("/me", response_model=UserResponse)
async def get_me(
        user: User = Depends(current_user),
):
    """Получить данные текущего пользователя, после авторизации"""
    return user
