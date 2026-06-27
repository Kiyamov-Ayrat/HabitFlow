from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import settings

# bcrypt — стандарт хеширования паролей.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Подписи JWT
ALGORITHM = "HS256"

def hash_password(plain_password: str) -> str:
    """Хешируем пароль перед сохранением в БД"""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяем пароли при логине"""
    return pwd_context.verify(plain_password, hashed_password)

def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Внутрення функция создания JWT"""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def create_access_token(user_id: int) -> str:
    """
    Access token - короткоживущий токне (30 мин)
    Передается в каждом запросе в заголовке Authorization: Beatet token
    """
    return _create_token(
        data={"sub": str(user_id), "type": "access"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

def create_refresh_token(user_id: int) -> str:
    """
    Refresh token - долгоживущий (30 дней)
    Используетя, чтобы получить новый access token
    Хранится в Redis, чтобы можно было отозвать
    """
    return _create_token(
        data={"sub": str(user_id), "type": "refresh"},
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )

def decode_token(token: str) -> dict[str, Any]:
    """
    Декодирутся и валидирутеся токен
    Бросает JWTError если токен невалидный или просроченный
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise exc
