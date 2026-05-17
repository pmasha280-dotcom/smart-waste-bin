from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Конвертируем PostgreSQL URL в SQLite если нужно
database_url = settings.DATABASE_URL
if database_url and "postgresql" in database_url:
    # Если все еще PostgreSQL, заменяем на SQLite
    database_url = "sqlite:///./smart_waste.db"

# Для SQLite нужно добавить check_same_thread=False
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(database_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
