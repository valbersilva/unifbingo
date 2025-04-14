# 🧪 UniFBingo - Automated Testing Guide

This document explains how to run and maintain the test suite for the UniFBingo backend.
It includes setup, coverage, organization, test conventions, and usage of both `unittest` and `pytest`.

---

## ✅ Prerequisites

- Python 3.13+
- Django 5.2+
- Django REST Framework

Ensure you have a virtual environment activated:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Optional: Install `pytest` and Django plugin for advanced usage:
```bash
pip install pytest pytest-django
```

---

## 🧪 Running All Tests (Default - Django)

To execute all tests across all apps:
```bash
python manage.py test
```

Run tests for a specific app:
```bash
python manage.py test users
python manage.py test bingo_room
python manage.py test game_session
```

Verbose output:
```bash
python manage.py test -v 2
```

---

## 🧪 Running Tests with Pytest

First, create a `pytest.ini` file at the root of the Django project:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = bingo_backend.settings
python_files = tests.py test_*.py *_tests.py
```

To run all tests using pytest:
```bash
pytest
```

To run tests for a specific app:
```bash
pytest users/
pytest bingo_room/
pytest game_session/
```

Use verbose and coverage flags:
```bash
pytest -v --tb=short
pytest --cov=. --cov-report=term-missing
```

Pytest supports advanced fixtures and plugins, including:
- `pytest-django`
- `pytest-cov`
- `pytest-mock`
- `pytest-xdist`

---

## 📁 Test File Structure

```
users/
├── tests.py        # User auth, registration, permissions

game_session/
├── tests.py        # Game session, draw, bingo validation, history

bingo_room/
├── tests.py        # Room creation, participation, cards
```

---

## 🧪 Test Coverage (Implemented)

### users/tests.py
- ✅ User creation (public access)
- ✅ Token authentication
- ✅ User listing (admin only)
- ✅ Role assignment
- ✅ Forbidden actions by players

### bingo_room/tests.py
- ✅ Room creation (host)
- ✅ Restriction for players
- ✅ Room join/leave (player)
- ✅ Card creation after joining
- ✅ Deny card creation if not in room

### game_session/tests.py
- ✅ Create session (host)
- ✅ Draw next number
- ✅ Validate BINGO (invalid & valid)
- ✅ End session manually
- ✅ History auto-generated
- ✅ Prevent multiple winners

---

## 🧪 Test Tools and Suggestions

We are using Django's `unittest.TestCase` via `APITestCase` from DRF:
```python
from rest_framework.test import APITestCase
```

Each test method:
- Must start with `test_`
- Should be isolated
- Should not depend on order

Test naming convention:
```python
def test_player_cannot_access_admin_routes(self):
    ...
```

Pytest-friendly tests can be separated into `test_*.py` files and use fixtures:
```python
@pytest.mark.django_db
def test_card_creation(client, django_user_model):
    user = django_user_model.objects.create_user(username='u', password='p')
    ...
```

---

## 🧹 Tips

- Clean test DB is recreated automatically each run
- Use `.setUp()` to create shared state per class
- Use `reverse()` for dynamic endpoint URLs
- Use `HTTP_AUTHORIZATION='Token ' + token` for auth

---

## 🛠️ Debugging Failures

To re-run failing tests with detailed output:
```bash
python manage.py test -v 2
pytest -v
```

Use breakpoints (`import pdb; pdb.set_trace()`) to pause test execution.

---

## 🗂️ Future Test Areas

- [ ] Game ranking logic
- [ ] Reconnection behavior
- [ ] Concurrency testing
- [ ] Performance testing (if required)

---

# Contact Information

```
Developed for:
UniFBV Wyden <>
Developed by: Valber Silva <valber.l.p.silva@gmail.com>

Tests Author: Valber Silva <valber.l.p.silva@gmail.com>

README Author: Valber Silva <valber.l.p.silva@gmail.com>

