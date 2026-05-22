import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://waste_user:secure_password_123@localhost:5432/waste_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # ИСПРАВЛЕНО: CORS для разработки
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost"
    ]
    
    DEMO_USER_ID: int = 1

settings = Settings()
