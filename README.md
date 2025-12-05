# MEPhI-Link

**MEPhI-Link** — это веб‑сервис для управления мероприятиями и записями студентов, сделанный для групп МИФИ.  
Проект включает фронтенд (Vue + Vite) и бэкенд (FastAPI + SQLite), задеплоенные на GitHub Pages и Render.

---

## 🇷🇺 Описание (Russian)

### Возможности

- Регистрация и авторизация пользователей
- Личный кабинет с:
  - личной информацией (ФИО, email, Telegram, курс, группа)
  - списком записей на мероприятия
  - списком созданных мероприятий (для админов / старост)
- Роли пользователей:
  - обычный студент
  - староста группы (может создавать мероприятия для своей группы)
  - администратор (может назначать роли и управлять пользователями)
- Мероприятия:
  - создание мероприятий с временем начала/окончания и количеством мест
  - автоматическая генерация тайм‑слотов
  - запись студентов на свободные слоты
  - отмена записей
  - редактирование и удаление мероприятий организатором
- Админ‑панель:
  - просмотр всех пользователей
  - выдача ролей (student / starosta / admin)
  - удаление пользователей

### Технологии

- **Frontend**: Vue 3, Vite, Axios
- **Backend**: FastAPI, Uvicorn
- **База данных**: SQLite
- **Деплой**:
  - фронтенд — GitHub Pages + GitHub Actions
  - бэкенд — Render (Web Service)

---

### Структура проекта

```text
MEPhI-Link/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI приложение и маршруты
│   │   ├── database/        # модели, доступ к БД, init_db
│   │   └── utils.py         # хеширование паролей и т.п.
│   ├── mephi_link.db        # SQLite база данных
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # страницы (Login, Register, Dashboard, Profile, Admin, EventDetail)
│   │   ├── components/      # компоненты (Navigation, EventCard и др.)
│   │   └── config.js        # API_URL из переменных окружения
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── .github/
    └── workflows/
        └── deploy.yml       # CI/CD для GitHub Pages
```

---

### Локальный запуск

#### 1. Клонирование репозитория

```bash
git clone https://github.com/MMenshikh/MEPhI-Link.git
cd MEPhI-Link
```

#### 2. Бэкенд

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# Запуск сервера
python -m uvicorn app.main:app --reload
```

Бэкенд будет доступен по адресу: `http://localhost:8000`  
Документация Swagger: `http://localhost:8000/docs`

#### 3. Фронтенд

В другом терминале:

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен по адресу: `http://localhost:5173`

---

### Переменные окружения (frontend)

В `frontend` используются переменные окружения Vite:

- `.env.development` — для локальной разработки
- `.env.production` — для продакшена

Пример:

```env
VITE_API_URL=http://localhost:8000
```

Фронтенд берёт URL бэкенда из `import.meta.env.VITE_API_URL` через файл `src/config.js`.

---

### CORS

В `backend/app/main.py` настроен CORS для локальной разработки и продакшена:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mmenshikh.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Деплой

#### Фронтенд (GitHub Pages)

- Сборка и деплой выполняются автоматически при пуше в ветку `main` через GitHub Actions (`.github/workflows/deploy.yml`).
- Собранный фронтенд публикуется в ветку `gh-pages` и доступен по адресу:

`https://mmenshikh.github.io/MEPhI-Link/`

#### Бэкенд (Render)

- Бэкенд развёрнут как Web Service на Render.
- Используется корневая директория `backend`, команда сборки:

```bash
pip install -r requirements.txt
```

- Команда запуска:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

- URL сервиса указывается во фронтенде через `VITE_API_URL` в `.env.production`.

---

## 🇬🇧 Description (English)

### Overview

**MEPhI-Link** is a small web service for managing events and student registrations, originally built for MEPhI groups.  
The project consists of a frontend (Vue + Vite) and a backend (FastAPI + SQLite), deployed to GitHub Pages and Render.

### Features

- User registration and login
- Personal account with:
  - personal info (name, email, Telegram, course, group)
  - list of registered events
  - list of created events (for admins / group leaders)
- User roles:
  - regular student
  - group leader (*starosta*) — can create events for their group
  - administrator — can assign roles and manage users
- Events:
  - create events with start/end time and slots count
  - automatic time slot generation
  - students can register for available slots
  - cancel registrations
  - organizers can edit and delete their events
- Admin panel:
  - view all users
  - assign roles (student / starosta / admin)
  - delete users

### Tech stack

- **Frontend**: Vue 3, Vite, Axios
- **Backend**: FastAPI, Uvicorn
- **Database**: SQLite
- **Deployment**:
  - frontend — GitHub Pages + GitHub Actions
  - backend — Render (Web Service)

---

### Project structure

```text
MEPhI-Link/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── database/        # models, DB access, init_db
│   │   └── utils.py         # password hashing, etc.
│   ├── mephi_link.db        # SQLite database
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # pages (Login, Register, Dashboard, Profile, Admin, EventDetail)
│   │   ├── components/      # components (Navigation, EventCard, etc.)
│   │   └── config.js        # API_URL from env variables
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── .github/
    └── workflows/
        └── deploy.yml       # CI/CD for GitHub Pages
```

---

### Local setup

#### 1. Clone repository

```bash
git clone https://github.com/MMenshikh/MEPhI-Link.git
cd MEPhI-Link
```

#### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

#### 3. Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

### Environment variables (frontend)

Vite uses environment files in `frontend`:

- `.env.development` — for local development
- `.env.production` — for production

Example:

```env
VITE_API_URL=http://localhost:8000
```

Frontend reads backend URL from `import.meta.env.VITE_API_URL` via `src/config.js`.

---

### CORS

In `backend/app/main.py`, CORS is configured for both local dev and production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mmenshikh.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Deployment

#### Frontend (GitHub Pages)

- Build and deployment are handled by GitHub Actions on push to `main` (see `.github/workflows/deploy.yml`).
- Built frontend is published to `gh-pages` and served at:

`https://mmenshikh.github.io/MEPhI-Link/`

#### Backend (Render)

- Backend is deployed as a Web Service on Render.
- Root directory: `backend`
- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

- Service URL is configured in frontend via `VITE_API_URL` in `.env.production`.

---

## License

Проект создан в учебных и личных целях для использования внутри студенческого сообщества МИФИ.  
The project is intended for educational and personal use within the MEPhI student community.