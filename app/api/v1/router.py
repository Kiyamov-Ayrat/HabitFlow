from fastapi import APIRouter
from app.api.v1.endpoints import auth, habits, completions, stats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(habits.router, prefix="/habits", tags=["Habits"])
api_router.include_router(completions.router, prefix="/completions", tags=["Completions"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])