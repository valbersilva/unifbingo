# UniFBingo Backend

REST API for managing an online bingo system with user roles, authentication, access control, and audit logging. Built with Django, Django REST Framework, and SQLite.

---

## 📦 Stack

- Python 3.13+
- Django 5.2+
- Django REST Framework
- SQLite (default)

---

## 🚀 Getting Started

### 1. Clone the project
```bash
git clone https://github.com/valbersilva/unifbingo.git
cd unifbingo/bingo_backend
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

(ou manualmente)
```bash
pip install django djangorestframework
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start server
```bash
python manage.py runserver
```

---

## 🔐 Authentication

Token-based authentication with Django REST Framework's TokenAuth.

### Login
**POST** `/api/login/`
```json
{
  "username": "adminuser",
  "password": "1234"
}
```
**Response**
```json
{
  "token": "<your-token>",
  "user_id": "uuid",
  "username": "adminuser",
  "role": "admin"
}
```
Use the token in requests:
```
Authorization: Token <your-token>
```

---

## 👥 Users API

Base URL: `/api/users/`

### Create user
**POST** `/api/users/`
```json
{
  "age": 25,
  "email": "email@example.com",
  "phone": "+559999999999",
  "username": "player1",
  "password": "1234"
}
```

### List all users *(admin only)*
**GET** `/api/users/`

### Get user by ID *(admin only)*
**GET** `/api/users/<uuid>/`

### Update user *(admin only)*
**PUT/PATCH** `/api/users/<uuid>/`

### Delete user *(admin only)*
**DELETE** `/api/users/<uuid>/`

### Change user role *(admin only)*
**PATCH** `/api/users/<uuid>/set_role/`
```json
{
  "role": "host"
}
```
Roles: `admin`, `host`, `player`

---

## 🛡️ Roles & Permissions

| Role     | Can Create Rooms | Can Play | Can Manage Users | Can Change Roles | Can See Logs |
|----------|------------------|----------|------------------|------------------|---------------|
| Admin    | ✅               | ✅       | ✅               | ✅               | ✅            |
| Host     | ✅               | ✅       | ❌               | ❌               | ❌            |
| Player   | ❌               | ✅       | ❌               | ❌               | ❌            |

---

## 📝 Audit Logs API

Base URL: `/api/audit-logs/`

**GET** `/api/audit-logs/` *(admin only)*

**Response**
```json
[
  {
    "id": "log-uuid",
    "actor_username": "admin1",
    "target_username": "player3",
    "action": "Changed role from player to host",
    "timestamp": "2025-04-13T21:00:00Z"
  }
]
```

Logs are created automatically for all role changes.

---

## 🏠 Bingo Room API

Base URL: `/api/bingo-rooms/`

### Create room *(host or admin only)*
**POST** `/api/bingo-rooms/`

### List all rooms
**GET** `/api/bingo-rooms/`

---

## 🎟️ Bingo Card API

Base URL: `/api/bingo-cards/`

### Create bingo card *(only if user is in the room)*
**POST** `/api/bingo-cards/`
```json
{
  "room": "<room-uuid>"
}
```

### List user bingo cards
**GET** `/api/bingo-cards/`

---

## 🙋 Room Participation API

### Join a room *(player only, and only one room at a time)*
**POST** `/api/join-room/`
```json
{
  "room": "<room-uuid>"
}
```

### Leave current room
**DELETE** `/api/leave-room/`

### Get current room
**GET** `/api/my-room/`

All of these actions are logged in the audit system.

---

## 🎮 Game Session API

Base URL: `/api/game-sessions/`

### Create game session
**POST** `/api/game-sessions/`
```json
{
  "room": "<room-uuid>"
}
```

### List all sessions
**GET** `/api/game-sessions/`

### Draw next number *(automatic, non-repeating)*
**POST** `/api/game-sessions/{session_id}/draw-next/`

**Response**
```json
{
  "id": "draw-uuid",
  "session": "game-session-id",
  "number": 42,
  "drawn_at": "2025-04-13T23:45:00Z"
}
```

### End session *(only creator or admin)*
**POST** `/api/game-sessions/{session_id}/end/`

**Response**
```json
{
  "detail": "Game session successfully ended."
}
```

### Validate bingo *(check if current user has a valid bingo)*
**POST** `/api/game-sessions/{session_id}/validate-bingo/`

**Responses**
```json
{ "detail": "BINGO! Valid row." }
{ "detail": "BINGO! Valid column." }
{ "detail": "BINGO! Valid main diagonal." }
{ "detail": "BINGO! Valid anti-diagonal." }
{ "detail": "BINGO is not valid." }
```

---

## 🔢 Drawn Numbers API

Base URL: `/api/drawn-numbers/`

### List all numbers for a session
**GET** `/api/drawn-numbers/?session={session_id}`

---

## 🧾 Game Audit Log API

Base URL: `/api/game-audit-logs/`

### List all logs for a session
**GET** `/api/game-audit-logs/?session={session_id}`

**Response**
```json
[
  {
    "id": "log-id",
    "session": "game-session-id",
    "actor_username": "host123",
    "action": "Drew number 42",
    "timestamp": "2025-04-13T23:45:00Z"
  }
]
```

This log is isolated from user audit and tracks only game events.

---

## 📂 Project Structure (simplificado)

```
unifbingo/
├── bingo_backend/        # Projeto Django
│   ├── settings.py
│   ├── urls.py
├── users/                # App principal
│   ├── models.py         # User e AuditLog
│   ├── views.py          # UserViewSet, Auth, AuditLogViewSet
│   ├── serializers.py
│   ├── permissions.py
│   ├── urls.py
├── bingo_room/
│   ├── models.py         # BingoRoom, BingoCard, RoomParticipant
│   ├── views.py          # BingoRoomViewSet, BingoCardViewSet, Join/Leave/MyRoom
│   ├── serializers.py    # Inclui RoomParticipantSerializer
│   ├── permissions.py    # IsHostOrAdmin
│   └── urls.py
├── game_session/
│   ├── models.py         # GameSession, DrawnNumber, GameAuditLog
│   ├── views.py          # Sorteio, encerramento e validação de bingo
│   ├── serializers.py
│   └── urls.py
```

---

## ✅ Todo (futuro)

- [ ] Registro de partidas
- [ ] Ranking e estatísticas

---

# Contact Information

```
Desenvolvido para:
UniFBV Wyden <>
Desenvolvido por: Valber Silva <valber.l.p.silva@gmail.com>

README Author: Valber Silva <valber.l.p.silva@gmail.com>
```
