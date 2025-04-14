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

## 📂 Project Structure (simplificado)

```
bingo_backend/
├── bingo_backend/        # Projeto Django
│   ├── settings.py
│   ├── urls.py
├── users/                # App principal
│   ├── models.py         # User e AuditLog
│   ├── views.py          # UserViewSet, Auth, AuditLogViewSet
│   ├── serializers.py
│   ├── permissions.py
│   ├── urls.py
├── db.sqlite3
```

---

## ✅ Todo (futuro)

- [ ] Sala de bingo (modelo e API)
- [ ] Geração de cartelas únicas com hash
- [ ] Participação em partidas
- [ ] Anúncio dos números sorteados
- [ ] Validação de bingo e histórico de partidas

---

# Contact Information

```
Desenvolvido para:
UniFBV Wyden <>
Desenvolvido por: Valber Silva <valber.l.p.silva@gmail.com>

README Author: Valber Silva <valber.l.p.silva@gmail.com>
```