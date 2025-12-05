# backend/make_admin.py
import sqlite3

conn = sqlite3.connect('mephi_link.db')
cur = conn.cursor()

email = "menshih.maksym@yandex.ru"

cur.execute("SELECT id, first_name, last_name, role, is_admin FROM users WHERE email = ?", (email,))
user = cur.fetchone()
print("Найден пользователь:", user)

if user:
    cur.execute("""
        UPDATE users
        SET is_admin = 1,
            role = 'admin'
        WHERE email = ?
    """, (email,))
    conn.commit()
    print("✅ Пользователь стал админом")
else:
    print("❌ Пользователь не найден")

conn.close()
