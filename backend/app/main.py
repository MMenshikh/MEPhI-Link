# backend/app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database.models import init_db
from app.database.db import UserDB, GroupDB, EventDB, SlotDB, RegistrationDB, get_db
from app.utils import hash_password, verify_password
import re

app = FastAPI(title="MEPhI-Link API", version="1.0.0")

# CORS для фронтенда на localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://mmenshikh.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Инициализация БД при старте приложения."""
    init_db()


# =============== АУТЕНТИФИКАЦИЯ ===============

@app.post("/api/auth/register")
async def register(request: Request):
    """Регистрация нового пользователя."""
    user = await request.json()

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "password",
        "telegram_alias",
        "course",
        "group_name",
    ]
    for field in required_fields:
        if field not in user or user[field] == "":
            raise HTTPException(
                status_code=400, detail=f"❌ Поле '{field}' обязательно")

    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", user["email"]):
        raise HTTPException(status_code=400, detail="❌ Некорректный email")

    if len(user["password"]) < 6:
        raise HTTPException(
            status_code=400, detail="❌ Пароль минимум 6 символов")

    if UserDB.get_user_by_email(user["email"]):
        raise HTTPException(
            status_code=400, detail="❌ Email уже зарегистрирован")

    password_hash = hash_password(user["password"])

    user_id = UserDB.create_user(
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"],
        password_hash=password_hash,
        telegram_alias=user["telegram_alias"],
        course=int(user["course"]),
        group_name=user["group_name"],
    )

    if not user_id:
        raise HTTPException(status_code=400, detail="❌ Ошибка при регистрации")

    return {
        "success": True,
        "message": "✅ Регистрация успешна!",
        "user_id": user_id,
    }


@app.post("/api/auth/login")
async def login(request: Request):
    """Авторизация пользователя."""
    credentials = await request.json()
    email = credentials.get("email")
    password = credentials.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=400, detail="❌ Email и пароль обязательны")

    user = UserDB.get_user_by_email(email)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=401, detail="❌ Неверный email или пароль")

    return {
        "success": True,
        "user_id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "group_name": user["group_name"],
        "is_admin": bool(user["is_admin"]),
        "role": user.get("role", "student"),
        "course": user["course"],
        "telegram_alias": user["telegram_alias"]
    }


# =============== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===============

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    """Получить данные пользователя по id."""
    user = UserDB.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="❌ Пользователь не найден")

    return {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "telegram_alias": user["telegram_alias"],
        "course": user["course"],
        "group_name": user["group_name"],
        "is_admin": bool(user["is_admin"]),
    }


# =============== ГРУППЫ ===============

@app.get("/api/groups")
async def get_groups():
    """Получить список групп."""
    groups = GroupDB.get_all_groups()
    return {"groups": groups}


# =============== МЕРОПРИЯТИЯ ===============

@app.post("/api/events")
async def create_event(request: Request, user_id: int):
    """Создать мероприятие (только админ/староста)."""
    body = await request.json()
    title = body.get("title")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    total_slots = body.get("total_slots")

    if not title or not start_time or not end_time or total_slots is None:
        raise HTTPException(
            status_code=400, detail="❌ Все поля мероприятия обязательны")

    user = UserDB.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="❌ Пользователь не найден")

    # 🔑 ИСПРАВЛЕНИЕ: используем .get() чтобы не было None
    user_role = user.get("role", "student")
    if user_role not in ["admin", "starosta"]:
        raise HTTPException(
            status_code=403, detail=f"❌ Только админы и старосты могут создавать мероприятия (ваша роль: {user_role})")

    if not re.match(r"^\d{2}:\d{2}$", start_time) or not re.match(r"^\d{2}:\d{2}$", end_time):
        raise HTTPException(
            status_code=400, detail="❌ Неверный формат времени (HH:MM)")

    event_id = EventDB.create_event(
        title=title,
        start_time=start_time,
        end_time=end_time,
        total_slots=int(total_slots),
        group_name=user["group_name"],
        organizer_id=user_id,
    )

    SlotDB.create_slots(event_id, start_time, end_time)

    return {
        "success": True,
        "event_id": event_id,
        "message": "✅ Мероприятие создано!",
    }


@app.get("/api/events/group/{group_name}")
async def get_events_by_group(group_name: str):
    """Получить все мероприятия для конкретной группы."""
    events = EventDB.get_events_by_group(group_name)
    return {"events": events}


@app.get("/api/events/{event_id}")
async def get_event(event_id: int):
    """Получить детали мероприятия и его слоты."""
    event = EventDB.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="❌ Мероприятие не найдено")

    slots = SlotDB.get_slots_by_event(event_id)
    return {
        "event": event,
        "slots": slots,
    }


@app.put("/api/events/{event_id}")
async def update_event(event_id: int, request: Request, user_id: int):
    """Обновить мероприятие (только создатель)."""
    body = await request.json()
    title = body.get("title")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    total_slots = body.get("total_slots")

    if not title or not start_time or not end_time or total_slots is None:
        raise HTTPException(status_code=400, detail="❌ Все поля обязательны")

    existing_event = EventDB.get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(status_code=404, detail="❌ Мероприятие не найдено")

    if existing_event["organizer_id"] != user_id:
        raise HTTPException(
            status_code=403, detail="❌ Вы не можете редактировать это мероприятие")

    # 1) Обновляем мероприятие
    EventDB.update_event(
        event_id=event_id,
        title=title,
        start_time=start_time,
        end_time=end_time,
        total_slots=int(total_slots),
    )

    # 2) Удаляем ВСЕ регистрации (записи студентов) на это мероприятие
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM registrations WHERE event_id = ?', (event_id,))
        conn.commit()

    # 3) Пересоздаём тайм-слоты
    SlotDB.delete_slots_by_event(event_id)
    SlotDB.create_slots(event_id, start_time, end_time)

    return {
        "success": True,
        "message": "✅ Мероприятие обновлено! Все записи отменены."
    }


@app.delete("/api/events/{event_id}")
async def delete_event(event_id: int, user_id: int):
    """Удалить мероприятие (только создатель)."""
    existing_event = EventDB.get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(status_code=404, detail="❌ Мероприятие не найдено")

    if existing_event["organizer_id"] != user_id:
        raise HTTPException(
            status_code=403, detail="❌ Вы не можете удалить это мероприятие")

    EventDB.delete_event(event_id)
    return {"success": True, "message": "✅ Мероприятие удалено!"}


@app.get("/api/events/organizer/{user_id}")
async def get_user_events(user_id: int):
    """Получить мероприятия, созданные пользователем."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE organizer_id = ?", (user_id,))
        events = [dict(row) for row in cursor.fetchall()]
    return {"events": events}


# =============== ЗАПИСИ НА СЛОТЫ ===============

@app.post("/api/registrations")
async def register_for_event(user_id: int, event_id: int, time_slot_id: int):
    """Записать пользователя на слот мероприятия."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM registrations WHERE user_id = ? AND event_id = ?",
            (user_id, event_id),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400, detail="❌ Вы уже записаны на это мероприятие")

    if RegistrationDB.register_user(user_id, event_id, time_slot_id):
        return {"success": True, "message": "✅ Вы записались!"}
    else:
        raise HTTPException(status_code=400, detail="❌ Этот слот уже занят")


@app.get("/api/registrations/{user_id}")
async def get_user_registrations(user_id: int):
    """Получить все записи пользователя."""
    registrations = RegistrationDB.get_user_registrations(user_id)

    result = []
    for reg in registrations:
        result.append({
            "id": reg["id"],
            "event_id": reg["event_id"],
            "title": reg["title"],
            "start_time": reg["start_time"],
            "end_time": reg["end_time"],
            "slot_time": reg["slot_time"],
            "time_slot_id": reg["time_slot_id"]
        })

    return {"registrations": result}


@app.delete("/api/registrations/{registration_id}/{time_slot_id}")
async def cancel_registration(registration_id: int, time_slot_id: int):
    """Отменить запись пользователя на слот."""
    try:
        RegistrationDB.cancel_registration(registration_id, time_slot_id)
        return {"success": True, "message": "✅ Запись отменена!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Ошибка: {str(e)}")


# =============== АДМИН-ПАНЕЛЬ ===============

@app.post("/api/admin/make-admin")
async def make_admin(request: Request, admin_id: int):
    """Выдать роль пользователю (только админ)."""
    body = await request.json()
    user_id = body.get("user_id")
    role = body.get("role", "student")

    if not user_id:
        raise HTTPException(status_code=400, detail="❌ user_id обязателен")

    admin_user = UserDB.get_user_by_id(admin_id)
    if not admin_user or admin_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="❌ Только администраторы могут выдавать роли")

    UserDB.set_user_role(int(user_id), role)

    # is_admin = 1 только если role == "admin"
    with get_db() as conn:
        cursor = conn.cursor()
        is_admin_value = 1 if role == "admin" else 0
        cursor.execute(
            'UPDATE users SET is_admin = ? WHERE id = ?',
            (is_admin_value, int(user_id))
        )
        conn.commit()

    return {"success": True, "message": f"✅ Роль {role} выдана!"}


@app.get("/api/admin/users")
async def get_all_users(admin_id: int):
    """Получить список всех пользователей (только админ)."""
    admin_user = UserDB.get_user_by_id(admin_id)
    if not admin_user or admin_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="❌ Только администраторы могут просматривать пользователей")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, first_name, last_name, email, group_name, role, is_admin "
            "FROM users ORDER BY created_at DESC"
        )
        users = [dict(row) for row in cursor.fetchall()]

    return {"users": users}


@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, admin_id: int):
    """Удалить пользователя (только админ)."""
    admin_user = UserDB.get_user_by_id(admin_id)
    if not admin_user or not admin_user["is_admin"]:
        raise HTTPException(
            status_code=403, detail="❌ Только администраторы могут удалять пользователей")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM registrations WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM events WHERE organizer_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    return {"success": True, "message": "✅ Пользователь удалён!"}


# =============== ROOT ===============

@app.get("/")
async def root():
    """Простой health-check."""
    return {"message": "🚀 MEPhI-Link API запущен!", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
