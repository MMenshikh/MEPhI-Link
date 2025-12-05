# backend/app/database/models.py
import sqlite3
from datetime import datetime


def init_db():
    """Инициализирует БД со всеми таблицами"""
    conn = sqlite3.connect('mephi_link.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                telegram_alias TEXT,
                course INTEGER,
                group_name TEXT,
                role TEXT DEFAULT 'student',
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # Таблица групп
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Таблица мероприятий (создаёт старост)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        total_slots INTEGER NOT NULL,
        group_name TEXT NOT NULL,
        organizer_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizer_id) REFERENCES users(id)
    )
    ''')

    # Таблица временных слотов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS time_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        slot_time TEXT NOT NULL,
        is_available BOOLEAN DEFAULT 1,
        FOREIGN KEY (event_id) REFERENCES events(id)
    )
    ''')

    # Таблица записей студентов на слоты
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        time_slot_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, event_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
        FOREIGN KEY (event_id) REFERENCES events(id)
    )
    ''')

    # Добавляем группы
    groups = [f'Б-{100+i}' for i in range(10)]
    for group in groups:
        cursor.execute(
            'INSERT OR IGNORE INTO groups (name) VALUES (?)', (group,))

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована!")


if __name__ == '__main__':
    init_db()
