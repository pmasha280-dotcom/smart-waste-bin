import jwt
from datetime import datetime
import sys

sys.path.insert(0, 'C:\\Users\\Maria\\smart-waste-bin\\backend')

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc3OTAyODY0M30.NTrs00XP1-lg0k-Z_y4g-okb3JIZYzp79atfkZyVnFs'

print("=== TOKEN DEBUG ===")
print(f"Token: {token[:50]}...")

# Декодируем без проверки
try:
    decoded = jwt.decode(token, options={'verify_signature': False})
    print(f"\nPayload: {decoded}")
    print(f"sub (user_id): {decoded.get('sub')} (type: {type(decoded.get('sub')).__name__})")
    print(f"exp: {decoded.get('exp')}")
    
    exp_time = datetime.fromtimestamp(decoded.get('exp'))
    now = datetime.now()
    print(f"Expires: {exp_time}")
    print(f"Now: {now}")
    print(f"Expired: {exp_time < now}")
    
except Exception as e:
    print(f"Decode error: {e}")

# Проверяем с секретом из настроек
try:
    from app.config import settings
    print(f"\nSECRET_KEY: {settings.SECRET_KEY[:20]}...")
    print(f"ALGORITHM: {settings.ALGORITHM}")
    
    verified = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"\n✅ TOKEN VALID!")
    print(f"Verified payload: {verified}")
    
except jwt.InvalidTokenError as e:
    print(f"\n❌ Invalid token: {e}")
except Exception as e:
    print(f"\nError: {e}")
