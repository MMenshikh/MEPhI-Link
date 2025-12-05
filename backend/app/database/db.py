# backend/app/database/db.py
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any

DATABASE = 'mephi_link.db'


@contextmanager
def get_db():
    """Контекстный менеджер для безопасной работы с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class UserDB:
    @staticmethod
    def create_user(first_name, last_name, email, password_hash, telegram_alias, course, group_name):
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (first_name, last_name, email, password, telegram_alias, course, group_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (first_name, last_name, email, password_hash, telegram_alias, course, group_name))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    @staticmethod
    def get_user_by_email(email):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_user_by_id(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def set_user_role(user_id, role):
        """Установить роль пользователю (admin, starosta, student)"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET role = ? WHERE id = ?', (role, user_id))
            conn.commit()

    @staticmethod
    def make_admin(user_id):
        """Сделать пользователя админом (для обратной совместимости)"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET role = ?, is_admin = 1 WHERE id = ?', ("admin", user_id))
            conn.commit()



class GroupDB:
    @staticmethod
    def get_all_groups():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM groups ORDER BY name')
            return [row[0] for row in cursor.fetchall()]


class EventDB:
    @staticmethod
    def create_event(title, start_time, end_time, total_slots, group_name, organizer_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (title, start_time, end_time, total_slots, group_name, organizer_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, start_time, end_time, total_slots, group_name, organizer_id))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_events_by_group(group_name):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM events WHERE group_name = ? ORDER BY created_at DESC', (group_name,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_event_by_id(event_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_event(event_id, title, start_time, end_time, total_slots):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE events SET title = ?, start_time = ?, end_time = ?, total_slots = ?
                WHERE id = ?
            ''', (title, start_time, end_time, total_slots, event_id))
            conn.commit()

    @staticmethod
    def delete_event(event_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM registrations WHERE event_id = ?', (event_id,))
            cursor.execute(
                'DELETE FROM time_slots WHERE event_id = ?', (event_id,))
            cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
            conn.commit()


class SlotDB:
    @staticmethod
    def create_slots(event_id, start_time, end_time):
        """Генерирует слоты по 30 минут"""
        from datetime import datetime, timedelta

        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")

        with get_db() as conn:
            cursor = conn.cursor()
            current = start
            slots = []

            while current < end:
                slot_time = current.strftime("%H:%M")
                cursor.execute('''
                    INSERT INTO time_slots (event_id, slot_time, is_available)
                    VALUES (?, ?, 1)
                ''', (event_id, slot_time))
                slots.append(slot_time)
                current += timedelta(minutes=30)

            conn.commit()
            return slots

    @staticmethod
    def get_slots_by_event(event_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, slot_time, is_available FROM time_slots 
                WHERE event_id = ? ORDER BY slot_time
            ''', (event_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_slots_by_event(event_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM time_slots WHERE event_id = ?', (event_id,))
            conn.commit()

class RegistrationDB:
    @staticmethod
    def register_user(user_id, event_id, time_slot_id):
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO registrations (user_id, event_id, time_slot_id)
                    VALUES (?, ?, ?)
                ''', (user_id, event_id, time_slot_id))
                
                cursor.execute('UPDATE time_slots SET is_available = 0 WHERE id = ?', (time_slot_id,))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    @staticmethod
    def get_user_registrations(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    r.id, 
                    e.id as event_id, 
                    e.title, 
                    e.start_time, 
                    e.end_time, 
                    ts.slot_time, 
                    ts.id as time_slot_id, 
                    e.group_name
                FROM registrations r
                JOIN events e ON r.event_id = e.id
                JOIN time_slots ts ON r.time_slot_id = ts.id
                WHERE r.user_id = ?
                ORDER BY e.created_at DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def cancel_registration(registration_id, time_slot_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM registrations WHERE id = ?', (registration_id,))
            cursor.execute('UPDATE time_slots SET is_available = 1 WHERE id = ?', (time_slot_id,))
            conn.commit()
