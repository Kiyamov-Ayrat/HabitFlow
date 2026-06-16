from pydantic import BaseModel

class HabitStats(BaseModel):
    habit_id: int
    title: str
    current_streak: int # текущая серия дней
    longest_streak: int #Рекорд
    total_completions: int #всего выполнений
    completion_rate: float # процент выполнения за 30 дней

class StatsResponse(BaseModel):
    habits: list[HabitStats]
    total_habits: int
    active_habits: int

