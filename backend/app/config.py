from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Database - используем SQLite вместо PostgreSQL
    DATABASE_URL: str = "sqlite:///./smart_waste.db"
    SECRET_KEY: str = "your-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - разрешаем все для разработки
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Demo user
    DEMO_USER_ID: int = 1

    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорируем дополнительные поля

settings = Settings()
