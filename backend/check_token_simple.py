import jwt

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc3OTAyODY0M30.NTrs00XP1-lg0k-Z_y4g-okb3JIZYzp79atfkZyVnFs'

print("=== TOKEN CHECK ===")
try:
    payload = jwt.decode(token, options={'verify_signature': False})
    print(f"Token payload: {payload}")
    print(f"User ID: {payload.get('sub')}")
    print(f"Expires: {payload.get('exp')}")
except Exception as e:
    print(f"Error: {e}")
