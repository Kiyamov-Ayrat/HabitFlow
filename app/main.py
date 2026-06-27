from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.settings import settings
from app.db.redis import redis_client
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Проверка подключения к БД при старте
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)
    # Проверка Redis
    await redis_client.ping()
    print("DB and Redis connect")

    yield

    # закрываем пул соединений
    await engine.dispose()
    await redis_client.close()
    print("Close connection")

app = FastAPI(
    title="HabitFlow API",
    version = '0.1.0',
    docs_url = "/api/docs",
    redoc_url = "/api/redoc",
    lifespan = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")