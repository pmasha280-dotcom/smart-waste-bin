import sys
import os

sys.path.insert(0, os.getcwd())
os.environ['DATABASE_URL'] = 'sqlite:///./smart_waste.db'

from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
try:
    # Создаем admin пользователя
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=pwd_context.hash("admin123"),
        is_active=True,
        is_superuser=True,
        role="admin"
    )
    db.add(admin)
    db.commit()
    print("✅ Admin пользователь успешно создан!")
    print("   Username: admin")
    print("   Password: admin123")
    
    # Проверяем, что добавился
    check = db.query(User).filter(User.username == "admin").first()
    if check:
        print(f"\n✅ Проверка: пользователь {check.username} существует в БД")
        print(f"   ID: {check.id}")
        print(f"   Роль: {check.role}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
