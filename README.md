# User Management System — Flask + MySQL

A full-stack starter project for creating, viewing, editing, searching, and deleting user records through a web dashboard and REST API.

## Features
- CRUD operations for user records
- Flask REST API with JSON responses
- SQLAlchemy persistence; MySQL configurable, SQLite fallback for quick local setup
- Input validation and duplicate-email handling
- Password hashing for passwords supplied at user creation (this is not a login/authentication system)
- Search by name, email, or role
- Automated tests using an in-memory SQLite database

## Run in VS Code (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the same terminal, then activate again.

By default, the app uses `instance/user_management.db` (SQLite), so it can run without installing MySQL.

## Configure MySQL (optional)
1. Create a database:
```sql
CREATE DATABASE user_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2. Copy `.env.example` to `.env`.
3. Set `DATABASE_URL` in `.env`:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/user_management_db
SECRET_KEY=replace-with-a-long-random-secret
```
4. Install dependencies and run `python run.py`. The app creates its tables at startup.

## REST API
Base path: `/api/users`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/users` | List users; optional `?q=search-term` |
| POST | `/api/users` | Create user |
| GET | `/api/users/<id>` | Retrieve one user |
| PUT/PATCH | `/api/users/<id>` | Update user |
| DELETE | `/api/users/<id>` | Delete user |
| GET | `/health` | Health check |

Example JSON for `POST /api/users`:
```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "role": "Developer",
  "password": "demo-password-123"
}
```
Passwords are hashed and never included in API responses.

## Tests
```powershell
python -m pytest -v
```

## Security / scope
This is a portfolio demo. It does not implement login, session authentication, role-based authorization, CSRF protection, or production deployment hardening. Do not use it for real personal data until those controls are added. Never commit `.env`, database files, or credentials.
