from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas import UserLogin, Token, UserResponse, UserRegister, InviteKeyCreate, InviteKeyResponse
from app.models import User, UserRole, InviteKey
from app.services.auth_service import AuthService
from app.dependencies import get_current_admin
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/demo", response_model=Token)
async def demo_login(
    db: Session = Depends(get_db)
):
    demo_user = db.query(User).filter(User.role == UserRole.GUEST).first()
    if not demo_user:
        # Create demo user if doesn't exist
        demo_user = User(
            username="demo_user",
            email="demo@smartbins.com",
            role=UserRole.GUEST,
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    
    access_token = AuthService.create_access_token(data={"sub": demo_user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(demo_user)
    )

@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Проверяем инвайт-ключ
    invite = db.query(InviteKey).filter(
        InviteKey.key == user_data.invite_key,
        InviteKey.is_active == True,
        InviteKey.used_by == None
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный или уже использованный инвайт-ключ"
        )
    
    # Проверяем срок действия
    if invite.expires_at and invite.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия инвайт-ключа истек"
        )
    
    # Проверяем, не занят ли username/email
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username или email уже зарегистрированы"
        )
    
    # Создаем пользователя с ролью из инвайт-ключа
    hashed_password = AuthService.get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=invite.role  # Роль берется из ключа!
    )
    
    db.add(user)
    db.flush()
    
    # Отмечаем ключ как использованный
    invite.used_by = user.id
    invite.used_at = datetime.now()
    invite.is_active = False
    
    db.commit()
    db.refresh(user)
    
    # Сразу выдаем токен
    access_token = AuthService.create_access_token(data={"sub": user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/invite-keys", response_model=InviteKeyResponse)
async def create_invite_key(
    key_data: InviteKeyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)  # Только админ может создавать ключи
):
    """Создание инвайт-ключа (только для админов)"""
    
    # Генерируем уникальный ключ
    key = secrets.token_urlsafe(32)
    
    expires_at = None
    if key_data.expires_days:
        expires_at = datetime.now() + timedelta(days=key_data.expires_days)
    
    invite_key = InviteKey(
        key=key,
        role=key_data.role,
        expires_at=expires_at
    )
    
    db.add(invite_key)
    db.commit()
    db.refresh(invite_key)
    
    return invite_key

@router.get("/invite-keys")
async def list_invite_keys(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Список всех инвайт-ключей (только для админов)"""
    keys = db.query(InviteKey).order_by(InviteKey.created_at.desc()).all()
    return keys

@router.delete("/invite-keys/{key_id}")
async def delete_invite_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Удаление инвайт-ключа (только для админов)"""
    key = db.query(InviteKey).filter(InviteKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    db.delete(key)
    db.commit()
    
    return {"message": "Key deleted successfully"}

@router.post("/init-first-admin")
async def init_first_admin(
    db: Session = Depends(get_db)
):
    """Инициализация первого администратора (только при пустой БД)"""
    
    # Проверяем, есть ли уже админы
    admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Администратор уже существует"
        )
    
    # Создаем первого администратора
    hashed_password = AuthService.get_password_hash("admin123")
    admin = User(
        username="admin",
        email="admin@smartbins.com",
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Создаем тестовые инвайт-ключи
    worker_key = InviteKey(
        key="WORKER_KEY_123",
        role=UserRole.WORKER,
        expires_at=datetime.now() + timedelta(days=30)
    )
    
    admin_key = InviteKey(
        key="ADMIN_KEY_123",
        role=UserRole.ADMIN,
        expires_at=datetime.now() + timedelta(days=30)
    )
    
    db.add(worker_key)
    db.add(admin_key)
    db.commit()
    
    return {
        "message": "Первый администратор создан",
        "admin_credentials": {"username": "admin", "password": "admin123"},
        "invite_keys": {
            "worker": "WORKER_KEY_123",
            "admin": "ADMIN_KEY_123"
        }
    }