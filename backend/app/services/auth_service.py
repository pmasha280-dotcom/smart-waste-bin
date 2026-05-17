import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля через bcrypt"""
        if not hashed_password:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля через bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """Аутентификация пользователя"""
        print(f"Authenticating user: {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"User {username} not found")
            return None
            
        print(f"User found: {user.username}, role: {user.role}")
        
        if not AuthService.verify_password(password, user.hashed_password):
            print(f"Password verification failed for {username}")
            return None
            
        print(f"User {username} authenticated successfully")
        return user

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Создание JWT токена - sub должен быть строкой"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        # Убеждаемся, что sub - строка
        if 'sub' in to_encode:
            to_encode['sub'] = str(to_encode['sub'])
            
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
