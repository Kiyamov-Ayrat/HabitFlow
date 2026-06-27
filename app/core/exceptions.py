from dataclasses import dataclass, field

@dataclass
class AppError(Exception):
    """Базовый класс для всех ошибок проекта"""
    message: str
    status_code: int = field(default=400, init=False)

@dataclass
class NotFoundError(AppError):
    """Ресурс не найден - ошибка 404"""
    status_code: int = field(default=404, init=False)

@dataclass
class ConflictError(AppError):
    """Конфликт данных (email занят) - ошибка 409"""
    status_code: int = field(default=409, init=False)

@dataclass
class UnauthorizedError(AppError):
    """Не авторизован (нет/плохой токен) ошибка 401"""
    status_code: int = field(default=401, init=False)

@dataclass
class ForbiddenError(AppError):
    """Нет прав на действие ошибка 403"""
    status_code: int = field(default=403, init=False)

