import sqlite3

conn = sqlite3.connect('mephi_link.db')
cursor = conn.cursor()

cursor.execute('UPDATE users SET role = ?, is_admin = 1 WHERE id = 1', ('admin',))
conn.commit()
conn.close()

print("✅ user_id=1 теперь админ с role='admin'")
