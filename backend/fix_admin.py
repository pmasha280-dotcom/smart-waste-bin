import sqlite3
import bcrypt

print("Подключение к БД...")
conn = sqlite3.connect('smart_waste.db')
cursor = conn.cursor()

# 1. Проверяем текущие данные
print("\n1. Текущие данные:")
cursor.execute("SELECT username, role, hashed_password FROM users WHERE username = 'admin'")
user = cursor.fetchone()
if user:
    print(f"   Username: {user[0]}")
    print(f"   Role: {user[1]}")
    print(f"   Hash: {user[2][:50]}...")
else:
    print("   Admin не найден!")

# 2. Обновляем роль на ADMIN
print("\n2. Обновляем роль...")
cursor.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
conn.commit()
print("   ✅ Роль обновлена на ADMIN")

# 3. Обновляем пароль с правильным bcrypt хешем
print("\n3. Обновляем пароль...")
password = b'admin123'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)
cursor.execute("UPDATE users SET hashed_password = ? WHERE username = 'admin'", (hashed.decode('utf-8'),))
conn.commit()
print(f"   ✅ Пароль обновлен. Новый хеш: {hashed.decode('utf-8')[:50]}...")

# 4. Проверяем результат
print("\n4. Проверка результата:")
cursor.execute("SELECT username, role, length(hashed_password) FROM users WHERE username = 'admin'")
user = cursor.fetchone()
print(f"   Username: {user[0]}")
print(f"   Role: {user[1]}")
print(f"   Hash length: {user[2]}")

conn.close()
print("\n✅ Готово! Теперь можно тестировать логин.")
