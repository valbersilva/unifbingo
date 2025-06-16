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

(or manually)
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

### 6. Expose in your network (optional)
```bash
python manage.py runserver 0.0.0.0:8000
```
Access it from other devices via:
```
http://<your-local-ip>:8000/
```
Make sure to add the IP to `ALLOWED_HOSTS` in `settings.py`.

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
  "email": "email@example.com",
  "username": "player1",
  "password": "1234"
}
```
Notes:
- Public requests (sem token) sempre criam usuários com:
  - `role = "player"`
  - `is_staff = false`
  - `is_superuser = false`
- Staffs autenticados podem criar usuários staff
- Admins autenticados podem criar outros admins
- Essas ações autenticadas são registradas no `AuditLog`

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

Logs are created automatically for all role changes and user creations feitas por usuários autenticados.

---

## 🏠 Bingo Room API

Base URL: `/api/bingo-rooms/`

### Create room *(host or admin only)*
**POST** `/api/bingo-rooms/`

### List all rooms

### Close room manually *(host or admin)*
**PATCH** `/api/close-room/<room-uuid>/`
Closes the room so that no new participants can join, even before a game session starts.
**GET** `/api/bingo-rooms/`

### New Features:
- Rooms are **automatically closed** when a game session starts. No new participants can join a closed room.
- Rooms can be **manually deleted** by their creator using `DELETE /api/delete-room/<room-uuid>/` if no game session is active.
- If a room becomes **empty** and has **no active game session**, it is **automatically deleted**.

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

> If a room is closed, join requests will be rejected.
> If all users leave and no active session exists, the room is deleted automatically.

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
> Creating a session automatically closes the associated room.

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
{ "detail": "🎉 BINGO! You are the winner by row." }
{ "detail": "🎉 BINGO! You are the winner by column." }
{ "detail": "🎉 BINGO! You are the winner by main diagonal." }
{ "detail": "🎉 BINGO! You are the winner by anti-diagonal." }
{ "detail": "BINGO is not valid." }
{ "detail": "A winner has already been declared." }
```

**Notes:**
- When a valid BINGO is found, the system automatically ends the session (`is_active = False`)
- The winner and winning card are saved in `winner` and `winning_card`
- An entry is added to `GameAuditLog`
- A new record is created in `GameHistory` with session details

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

## 🗃️ Game History API

Base URL: `/api/game-history/`

### List all historical games
**GET** `/api/game-history/`

**Response**
```json
[
  {
    "id": "history-uuid",
    "session": "session-uuid",
    "room_code": "ABC-123",
    "winner_username": "player1",
    "winning_card_hash": "abcdef123456...",
    "drawn_numbers": [5, 12, 33, 49, ...],
    "started_at": "2025-04-13T22:00:00Z",
    "ended_at": "2025-04-13T22:15:00Z",
    "is_completed": true
  }
]
```

This history is created automatically at the end of each game session.

---

## 📂 Project Structure (simplified)

```
unifbingo/
├── bingo_backend/        # Django Project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                # User management
│   ├── models.py         # User and AuditLog
│   ├── views.py          # UserViewSet, Auth, AuditLogViewSet
│   ├── serializers.py
│   ├── permissions.py
│   ├── urls.py
├── bingo_room/
│   ├── models.py         # BingoRoom, BingoCard, RoomParticipant
│   ├── views.py          # BingoRoomViewSet, BingoCardViewSet, Join/Leave/MyRoom
│   ├── serializers.py    # Includes RoomParticipantSerializer
│   ├── permissions.py    # IsHostOrAdmin
│   └── urls.py
├── game_session/
│   ├── models.py         # GameSession, DrawnNumber, GameAuditLog, GameHistory
│   ├── views.py          # Drawing, ending, bingo validation, history
│   ├── serializers.py
│   └── urls.py
```

---

## ✅ Todo (future)

- [ ] Ranking and player statistics

---

# Contact Information

```
Developed for:
UniFBV Wyden <>
Developed by: Valber Silva <valber.l.p.silva@gmail.com>
Humberto Matheus de Andrade Santana <humbertomatheuz@gmail.com>

README Author: Valber Silva <valber.l.p.silva@gmail.com>
```

