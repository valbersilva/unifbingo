# 🧪 UniFBingo - Automated Testing Guide

This document explains how to run and maintain the test suite for the UniFBingo backend.
It includes setup, coverage, organization, and test conventions.

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

---

## 🧪 Running All Tests

To execute all tests across all apps:
```bash
python manage.py test
```

You can run tests for a specific app:
```bash
python manage.py test users
python manage.py test bingo_room
python manage.py test game_session
```

To run tests in verbose mode:
```bash
python manage.py test -v 2
```

---

## 📁 Test File Structure

```
users/
├── tests.py        # User auth, registration, permissions

bingo_room/
├── tests.py        # Room creation, participation, cards

game_session/
├── tests.py        # Game session, draw, bingo validation, history
```

---

## 🧪 Test Coverage (implemented)

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