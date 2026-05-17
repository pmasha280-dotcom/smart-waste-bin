import sys
sys.path.insert(0, 'C:\\Users\\Maria\\smart-waste-bin\\backend')
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
if user:
    print(f"=== USER WITH ID=1 ===")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Is active: {user.is_active}")
    print(f"Hashed password: {user.hashed_password[:50]}...")
else:
    print("User with id=1 not found!")
    
# Также проверим всех пользователей
all_users = db.query(User).all()
print(f"\n=== ALL USERS ({len(all_users)}) ===")
for u in all_users:
    print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}, Active: {u.is_active}")
db.close()
