from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Данные для регистрации"""
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Возвращаем ответ клиенту без пароля"""
    id: int
    name: str
    email: EmailStr
    timezone: str

    # Чтение данных из ORM-объектов
    model_config = {"from attributes": True}

class TokenResponse(BaseModel):
    """Ответ при логине, пара токенов"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    """Тело запроса на обновление токена"""
    refresh_token: str
