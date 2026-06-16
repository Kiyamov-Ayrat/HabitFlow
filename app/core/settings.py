from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    app_debug: bool = False
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5433  # 5433 потому что 5432 занят локальным PostgreSQL

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl_seconds: int = 300

    # RabbitMQ
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672

    # Email
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@habitflow.app"
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_tls: bool = True

    @property
    def database_url(self) -> str:
        # asyncpg — для FastAPI (async)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        # psycopg v3 — для Alembic (sync)
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}//"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()