import sqlite3

conn = sqlite3.connect('smart_waste.db')
cursor = conn.cursor()

# Список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Таблицы в БД:")
for table in tables:
    print(f"  - {table[0]}")

# Структура таблицы users
try:
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print("\nСтруктура таблицы users:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")
except Exception as e:
    print(f"\nТаблица users не найдена: {e}")

# Количество пользователей
try:
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    print(f"\nВсего пользователей: {count}")
    
    cursor.execute("SELECT username, email, is_active FROM users;")
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user[0]} ({user[1]}), active: {user[2]}")
except Exception as e:
    print(f"Ошибка при чтении users: {e}")

conn.close()
