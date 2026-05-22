from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not hashed_password:
            return False
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        if 'sub' in to_encode:
            to_encode['sub'] = str(to_encode['sub'])
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
