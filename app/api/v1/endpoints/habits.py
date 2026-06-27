from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from app.services import habit as habit_service

router = APIRouter()

@router.get("/", response_model=list[HabitResponse])
async def get_habits(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """Получаем все привычки текущего пользователя"""
    return await habit_service.get_user_habits(user, db)

@router.post("/", response_model=HabitResponse, status_code=201)
async def create_habit(
        data: HabitCreate,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    """Создае новую привычку"""
    return await habit_service.create_habit(data, user, db)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
        habit_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    """Получаем привычку по id"""
    return await habit_service.get_habit_by_id(habit_id, user, db)

@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(
        habit_id: int,
        data: HabitUpdate,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    """Обновляем привычку, обновляются только переданные поля"""
    return await habit_service.update_habit(habit_id, data, user, db)

@router.delete("/{habit_id}", status_code=204)
async def delete_habit(
        habit_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    """Удаляем привычку вместе со всеми отметками"""
    await habit_service.delete_habit(habit_id, user, db)

