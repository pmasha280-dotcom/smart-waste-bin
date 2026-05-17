import sys
import os

# Добавляем путь к backend
sys.path.insert(0, r'C:\Users\Maria\smart-waste-bin\backend')
os.chdir(r'C:\Users\Maria\smart-waste-bin\backend')

# Устанавливаем переменную окружения
os.environ['DATABASE_URL'] = 'sqlite:///./smart_waste.db'

print("Importing modules...")
from app.database import engine, Base, SessionLocal
from app.models import User
from passlib.context import CryptContext

print("Creating tables...")
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

try:
    # Проверяем и создаем admin пользователя
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        print("Creating admin user...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print("✓ Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("✓ Admin user already exists")
    
    # Выводим список пользователей
    users = db.query(User).all()
    print(f"\nTotal users in database: {len(users)}")
    for user in users:
        print(f"  - {user.username} ({user.email})")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✓ Database initialization complete!")
